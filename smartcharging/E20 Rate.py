from matplotlib import pyplot as plt
import matplotlib

matplotlib.rc("lines", linewidth=2)

from cvxpower import Net, Group, Storage, Generator, Device, Terminal
import cvxpy as cvx
import pandas as pd
import numpy as np


class Grid(Generator):
    def __init__(self, energy_rate=None, demand_rate=None, **kwargs):
        self.rate_e = energy_rate[None]
        self.rate_d = demand_rate
        # self.energy = energy
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
        return cost

class EV(Storage):
    def __init__(self, charge_max=None, energy_final=None, **kwargs):
        charge_max = charge_max[:, None]
        super(EV, self).__init__(
            charge_max=charge_max,
            energy_max=energy_final,
            energy_final=energy_final,
            len_interval=0.25,
            **kwargs
        )

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
    retval[(index > arrival_time) & (index < departure_time)] = limit_kw
    return retval


start = pd.Timestamp("2020-03-09 00:00")
index = pd.date_range(start, start + pd.DateOffset(hours=24), freq="15min")[:-1]

vehicles = [
    EV(
        name="Alice",
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 08:00"), pd.Timestamp("2020-03-09 17:00"), limit_kw=6.6
        ),
        energy_init=23.0,
        energy_final=75.0,
    ),
    EV(
        name="Bob",
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 09:00"), pd.Timestamp("2020-03-09 17:45"), limit_kw=6.6
        ),
        energy_init=20.0,
        energy_final=50.0,
    ),
    EV(
        name="Carol",
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 06:00"), pd.Timestamp("2020-03-09 11:00"), limit_kw=3.3
        ),
        energy_init=0.0,
        energy_final=8.8,
    ),
]
grid = Grid(energy_rate=energy_rate(index), demand_rate=demand_rate(index))
net = Net([v.terminals[0] for v in vehicles] + [grid.terminals[0]])
network = Group(vehicles + [grid], [net])
results = network.optimize(time_horizon=len(index), verbose=True, solver="ECOS")
print(results)

prices = pd.DataFrame(energy_rate(index), index=index, columns=["E20"])
prices.plot()
plt.ylabel("Price ($/kWh)")

power = np.stack([v.terminals[0].power_var.value[:,0] for v in vehicles], axis=1)
names = [v.name for v in vehicles]
power = pd.DataFrame(power, index=index, columns=names)
np.maximum(power, 0.).plot.area(title='E20')
plt.ylabel("Power (kW)")
plt.show()

avg_price = np.sum((power.sum(axis=1) * energy_rate(index))) / np.sum(power.sum(axis=1))
print("Average price: $%.04f / kWh" % avg_price)


# rate_energy_peak = 0.16997
# rate_energy_partpeak = 0.12236
# rate_energy_offpeak = 0.09082
# rate_demand_peak = 21.23
# rate_demand_partpeak = 5.85
# rate_demand_overall = 19.10
#
# energy_prices = np.concatenate((np.repeat(rate_energy_offpeak, int(8.5*4)), np.repeat(rate_energy_partpeak, int(3.5*4)),
#                 np.repeat(rate_energy_peak, int(6*4)), np.repeat(rate_energy_partpeak, int(3.5*4)),
#                 np.repeat(rate_energy_offpeak, int(2.5*4))))
#
# peak_inds = np.arange(int(12*4), int(18*4))
# partpeak_inds = np.concatenate((np.arange(int(8.5*4), int(12*4)), np.arange(int(18*4), int(21.5*4))))
# offpeak_inds = np.concatenate((np.arange(0, int(8.5*4)), np.arange(int(21.5*4), int(24*4))))

# schedule = cvx.Variable((96, num_sessions))
# obj = cvx.matmul(cvx.sum(schedule, axis=1),  energy_prices.reshape((np.shape(energy_prices)[0], 1)))
# obj += rate_demand_overall*cvx.max(cvx.sum(schedule, axis=1))
# obj += rate_demand_peak*cvx.max(cvx.sum(schedule[peak_inds, :], axis=1))
# obj += rate_demand_partpeak*cvx.max(cvx.sum(schedule[partpeak_inds, :], axis=1))
#
# constraints = [schedule >= 0]
# for i in range(num_sessions):
#     constraints += [schedule[:, i] <= np.maximum(np.max(power[:, i]), charge_rate)]
#     if departure_inds[i] >= arrival_inds[i]:
#         if arrival_inds[i] > 0:
#             constraints += [schedule[np.arange(0, int(arrival_inds[i])), i] <= 0]
#         if departure_inds[i] < 96:
#             constraints += [schedule[np.arange(int(departure_inds[i]), 96), i] <= 0]
#     else:
#         constraints += [schedule[np.arange(int(departure_inds[i]), int(arrival_inds[i])), i] <= 0]
#
# energies = 0.25*np.sum(power, axis=0)
# max_energies = np.zeros((num_sessions, ))
# for i in range(num_sessions):
#     if departure_inds[i] >= arrival_inds[i]:
#         max_energies[i] = 0.25*charge_rate*(departure_inds[i]-arrival_inds[i])
#     else:
#         max_energies[i] = 0.25*charge_rate*((departure_inds[i])+(96-arrival_inds[i]))
# where_violation = np.where((max_energies-energies)<0)[0]
# print('Energy violation for ',len(where_violation),' of the sessions.')
# energies[where_violation] = max_energies[where_violation]
# constraints += [0.25*cvx.sum(schedule, axis=0)==energies]

# prob = cvx.Problem(cvx.Minimize(obj), constraints)
# result = prob.solve(cvx.MOSEK)