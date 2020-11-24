from matplotlib import pyplot as plt
import matplotlib

matplotlib.rc("lines", linewidth=2)

from cvxpower import Net, Group, Storage, Generator, Device, Terminal
import cvxpy as cvx
import pandas as pd
import numpy as np
from scipy.stats import norm
from .analyze.analyze import *

utility = 100
power_max_default = 100

class Grid(Generator):
    def __init__(self, energy_rate=None, demand_rate=None, **kwargs):
        self.rate_e = energy_rate[None]
        self.rate_d = demand_rate
        super(Grid, self).__init__(**kwargs)

    @property
    def cost(self):
        power = -self.terminals[0].power_var
        T, S = self.terminals[0].power_var.shape
        cost = cvx.sum(0.25 * power * np.reshape(self.rate_e, (1, 96)))
        cost += cvx.max(power[self.rate_d['max_demand_ind'][0]]) * self.rate_d['max_demand']
        cost += cvx.max(power[self.rate_d['max_peak_demand_ind'][0]]) * self.rate_d['max_peak_demand']
        cost += cvx.max(power[self.rate_d['max_part_peak_demand_ind'][0]]) * self.rate_d['max_part_peak_demand']
        cost = cvx.reshape(cost, (1, S))
        return cost

class Transformer(Device):
    def __init__(self, power_max=None):
        super(Transformer, self).__init__([Terminal(), Terminal()])
        self.power_max = power_max

    @property
    def constraints(self):
        p1 = self.terminals[0].power_var
        p2 = self.terminals[1].power_var
        constrs = [
            p1 + p2 == 0,
            cvx.abs((p1 - p2) / 2) <= self.power_max
        ]
        return constrs

# PG&E E-20
def energy_rate(index):
    retval = np.zeros(len(index))
    # PG&E E-19 rate structure: https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-19.pdf
    # off-peak
    retval[(index.hour*4 + index.minute/15 <= 8.5*4)] = 0.09496  # 0000 - 0830
    retval[(index.hour * 4 + index.minute / 15 > 21.5 * 4)] = 0.09496  # 2130 - 2345
    # partial peak
    retval[(index.hour * 4 + index.minute / 15 >= 8.5 * 4) & (index.hour < 13)] = 0.12656 # 0830 - 1200
    retval[(index.hour >= 18) & (index.hour * 4 + index.minute / 15 <= 21.5 * 4)] = 0.12656 # 1800 - 2130
    # peak-hours
    retval[(index.hour >= 12) & (index.hour < 18)] = 0.17427  # 1200 - 1800
    return retval

def demand_rate(index):
    max_demand_ind = [(index.hour*4 + index.minute/15 <= 24*4)]
    max_part_peak_demand_ind = [((index.hour * 4 + index.minute / 15 >= 8.5 * 4) & (index.hour < 13)) | ((index.hour >= 18) & (index.hour * 4 + index.minute / 15 <= 21.5 * 4))]
    max_peak_demand_ind = [(index.hour >= 12) & (index.hour < 18)]
    retval = {'max_demand': 21.10, 'max_part_peak_demand': 6.1, 'max_peak_demand': 21.94, 'max_demand_ind': max_demand_ind, 'max_part_peak_demand_ind':max_part_peak_demand_ind, 'max_peak_demand_ind': max_peak_demand_ind}
    return retval

'''
index: date range, separate by 15 mins interval
expected_departure: expected timestamp when the car will leave
Requirement of *kwargs: {'site_name': name, 'user_id':id}
Example {'site_name' : 'user_id':id}
'''
# Departure probability from the historical data analysis
predicter = ANALYZE()
predicter.setup('./analyze/historical_data/')
Group_dict = {
    'slac_GISMO' : 'SLAC', 
    'slac_B53' : 'SLAC', 
    'google_plymouth' : 'Google-Plymouth', 
    'google_B46' : 'Google-B46', 
    'google_CRIT' : 'Google-CRIT'
}
def departure_prob(index, site_name=None, user_id=None):
    density = np.zeros(len(index))
    if site_name and user_id is not None:    
        # if user_id in predicter.driver_model.user_id_set:
        #     distribution = predicter.driver_model.avg_stats_dict[user_id]['Departure']
        #     density = distribution / np.sum(distribution)
        # else:
        distribution = predicter.site_models[Group_dict[site_name]].avg_stats_dict['Departure']
        density = distribution / np.sum(distribution)
    return density

class EV(Storage):
    @property
    def cost(self):
        T, S = self.terminals[0].power_var.shape
        if self.energy is None:
            self.energy = cvx.Variable(self.terminals[0].power_var.shape)
        cost = -utility * self.departure_prob * self.energy
        cost = cvx.reshape(cost, (1, S))
        return cost

    def __init__(self, charge_max=None, energy_final=None, departure_prob=None, **kwargs):
        self.departure_prob = departure_prob
        super(EV, self).__init__(
            charge_max=charge_max,
            energy_max=energy_final,
            energy_final=energy_final,
            len_interval=0.25,
            **kwargs
        )

def get_vehicles(index, group_info, group):
    vehicles = []
    for session in group_info:
        vehicles.append( EV(
            name=session['user_id'],
            # Get from machine learning or set default distribution
            departure_prob=departure_prob(index, group, session['user_id']),
            # From first entry in the db when a user charging session starts = port_power
            charge_max=session['port_power'],
            # Change energy init according to current session energy
            energy_init=session['energy'],
            energy_final=100.0,
        ))
    return vehicles

def energy_opt(group_config, opt_input, none_user_power, fail_get_energy_cnt):
    db_write = []
    
    for group in opt_input:
        # No station in use, return directly
        group_info = opt_input[group]
        if not group_info:
            continue
        
        # start now and plan for 24 hours
        start = pd.Timestamp.now()
        index = pd.date_range(start, start + pd.DateOffset(hours=24), freq="15min")[:-1]
        
        # Init the Grid and transformer
        grid = Grid(energy_rate=energy_rate(index), demand_rate=demand_rate(index))

        # Get power_max from database
        power_max = power_max_default
        if group in group_config:
            power_max = group_config[group]
        # Get the total max consumed power from the userID=None station ports
        none_power_total = 0.0
        for none_user in none_user_power[group]:
            none_power_total += none_user['port_power']
        transformer = Transformer(power_max=power_max-none_power_total)
        
        # Get real-time EV list
        vehicles = get_vehicles(index, group_info, group)
        
        # Construct the network
        net_v = Net([v.terminals[0] for v in vehicles] + [transformer.terminals[0]], name="EVSE")
        net_g = Net([grid.terminals[0], transformer.terminals[1]], name="Grid")
        network = Group(vehicles + [grid, transformer], [net_v, net_g])
        print(group)
        
        # Optimize the network
        try:
            results = network.optimize(time_horizon=len(index), verbose=True, solver="ECOS")
        except Exception as e: 
            # TODO: wait for log format from @Zixiong log the failure
            print(e)
            continue
        # TODO: wait for log format from @Zixiong log the failure
        if results.status != 'optimal':
            continue
        power = [v.terminals[0].power_var.value[0][0] for v in vehicles]
        
        for i in range(len(vehicles)):
            # Send power to the station shed to opt_input and none_user_power
            # ret = cp.setStationLoad(stationIDs[i], ports[i], power[i])
            # TODO: wait for log format from @Zixiong If success or not log the failure
            # write into database (userId, success or fail, power, timestamp, stationid and port)
            tmp_output = {
                'user_id': group_info[i]['user_id'],
                'status': 'Fail',
                'power': power[i],
                'timestamp': pd.Timestamp.now(),
                'station_id': group_info[i]['station_id'],
                'port_number': group_info[i]['port_number'],
                'group_name': group
            }
            db_write.append(tmp_output)
    return db_write
