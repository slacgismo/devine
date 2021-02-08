from matplotlib import pyplot as plt
import matplotlib

matplotlib.rc("lines", linewidth=2)
# matplotlib.rc("figure", figsize=(16,6))

from cvxpower import Net, Group, Storage, Generator, Device, Terminal
import cvxpy as cvx
import pandas as pd
import numpy as np
from scipy.stats import norm

class Grid(Generator):
    def __init__(self, energy_rate=None, demand_rate=None, **kwargs):
        self.rate_e = energy_rate[None]
        self.rate_d = demand_rate
        super(Grid, self).__init__(**kwargs)

    @property
    def cost(self):
        power = -self.terminals[0].power_var
        T, S = self.terminals[0].power_var.shape
        # if self.energy is None:
        #     self.energy = cvx.Variable(self.terminals[0].power_var.shape)
        cost = cvx.sum(0.25 * power * np.reshape(self.rate_e, (1, 96)))
        cost += cvx.max(power[self.rate_d['max_demand_ind'][0]]) * self.rate_d['max_demand']
        cost += cvx.max(power[self.rate_d['max_peak_demand_ind'][0]]) * self.rate_d['max_peak_demand']
        cost += cvx.max(power[self.rate_d['max_part_peak_demand_ind'][0]]) * self.rate_d['max_part_peak_demand']
        cost = cvx.reshape(cost, (1, S))
        # cost = np.zeros(96)
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

def charge_max(index, arrival_time, departure_time, limit_kw):
    retval = np.zeros(len(index))
    # retval[(index > arrival_time) & (index < departure_time)] = limit_kw
    retval[(index > arrival_time)] = limit_kw
    return retval

start = pd.Timestamp("2020-03-09 00:00", tz="US/Pacific")  # Monday
index = pd.date_range(start, start + pd.DateOffset(hours=24), freq="15min")[:-1]
names = ["EV1", "EV2", "EV3", "EV4", "EV5", "EV6", "EV7", "EV8", "EV9", "EV10"]
departures = [
    pd.Timestamp("2020-03-09 11:17", tz="US/Pacific"),
    pd.Timestamp("2020-03-09 17:44", tz="US/Pacific"),
    pd.Timestamp("2020-03-09 16:22", tz="US/Pacific"),
    pd.Timestamp("2020-03-09 17:19", tz="US/Pacific"),
    pd.Timestamp("2020-03-09 17:20", tz="US/Pacific"),
    pd.Timestamp("2020-03-09 12:23", tz="US/Pacific"),
    pd.Timestamp("2020-03-09 13:38", tz="US/Pacific"),
    pd.Timestamp("2020-03-09 14:42", tz="US/Pacific"),
    pd.Timestamp("2020-03-09 16:28", tz="US/Pacific"),
    pd.Timestamp("2020-03-09 19:01", tz="US/Pacific")
]


def certain_schedule(index, departure):
    retval = np.zeros(len(index))
    retval[index > departure] = 1.
    return retval


def uncertain_schedule(index, departure, sigma=4):
    i = np.nonzero(index > departure)[0][0]
    return norm.cdf(np.arange(len(index)), loc=i, scale=4)


certain = pd.DataFrame(
    np.stack([certain_schedule(index, d) for d in departures], axis=1),
    index=index,
    columns=names)
certain.tz_localize(None).plot()
plt.ylabel("Departure Certain");

uncertain = pd.DataFrame(
    np.stack([uncertain_schedule(index, d) for d in departures], axis=1),
    index=index,
    columns=names)
uncertain.tz_localize(None).plot()
plt.ylabel("Departure Uncertain");

utility = 100


def departure_prob(index, expected_departure, sigma=4):
    i = np.nonzero(index > expected_departure)[0][0]
    prob = norm.pdf(np.arange(len(index)), loc=i, scale=sigma)
    prob = prob / np.sum(prob)
    return prob


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


start = pd.Timestamp("2020-03-09 00:00")
index = pd.date_range(start, start + pd.DateOffset(hours=24), freq="15min")[:-1]

vehicles = [
    EV(
        name="EV1", # UserID from CP
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 12:00")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 08:11"), pd.Timestamp("2020-03-09 11:17"), limit_kw=6.6)[None].transpose(),
        # charge_max=6.6,
        energy_init=23.0,
        energy_final=35.8,
    ),
    EV(
        name="EV2",
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 17:00")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 08:45"), pd.Timestamp("2020-03-09 17:44"), limit_kw=6.6)[None].transpose(),
        # charge_max=6.6,
        energy_init=20.0,
        energy_final=55.0,
    ),
    EV(
        name="EV3",
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 16:30")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 08:54"), pd.Timestamp("2020-03-09 16:22"), limit_kw=6.6)[None].transpose(),
        # charge_max=3.3,
        energy_init=0.0,
        energy_final=8.8,
    ),
EV(
        name="EV4",
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 17:00")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 09:00"), pd.Timestamp("2020-03-09 17:19"), limit_kw=6.6)[None].transpose(),
        # charge_max=3.3,
        energy_init=0.0,
        energy_final=13.8,
    ),
EV(
        name="EV5",
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 17:00")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 09:12"), pd.Timestamp("2020-03-09 17:20"), limit_kw=6.6)[None].transpose(),
        # charge_max=3.3,
        energy_init=0.0,
        energy_final=10.5,
    ),
EV(
        name="EV6",
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 13:00")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 09:37"), pd.Timestamp("2020-03-09 12:23"), limit_kw=6.6)[None].transpose(),
        # charge_max=3.3,
        energy_init=0.0,
        energy_final=6.4,
    ),
EV(
        name="EV7",
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 15:00")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 09:45"), pd.Timestamp("2020-03-09 13:38"), limit_kw=6.6)[None].transpose(),
        # charge_max=3.3,
        energy_init=0.0,
        energy_final=21.2,
    ),
EV(
        name="EV8",
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 15:00")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 10:23"), pd.Timestamp("2020-03-09 14:42"), limit_kw=6.6)[None].transpose(),
        # charge_max=3.3,
        energy_init=0.0,
        energy_final=11.8,
    ),
EV(
        name="EV9",
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 17:00")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 09:57"), pd.Timestamp("2020-03-09 16:28"), limit_kw=6.6)[None].transpose(),
        # charge_max=3.3,
        energy_init=0.0,
        energy_final=14.9,
    ),
EV(
        name="EV10",
        departure_prob=departure_prob(index, pd.Timestamp("2020-03-09 19:10")),
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 10:25"), pd.Timestamp("2020-03-09 19:01"), limit_kw=6.6)[None].transpose(),
        # charge_max=3.3,
        energy_init=0.0,
        energy_final=11.2,
    ),
]
grid = Grid(energy_rate=energy_rate(index), demand_rate=demand_rate(index))
transformer = Transformer(power_max=17)

net_v = Net([v.terminals[0] for v in vehicles] + [transformer.terminals[0]], name="EVSE")
net_g = Net([grid.terminals[0], transformer.terminals[1]], name="Grid")
network = Group(vehicles + [grid, transformer], [net_v, net_g])
results = network.optimize(time_horizon=len(index), verbose=True, solver="ECOS")
print(results)

power = np.stack([v.terminals[0].power_var.value[:, 0] for v in vehicles], axis=1)
names = [v.name for v in vehicles]
power = pd.DataFrame(power, index=index, columns=names)
np.maximum(power, 0.).plot.area(title='Uncertain Dep, Cap, E20')
plt.show()

avg_price = np.sum((power.sum(axis=1) * energy_rate(index))) / np.sum(power.sum(axis=1))

print("Average price: $%.04f / kWh" % avg_price)
print(power.sum() / 4.)
