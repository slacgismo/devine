from matplotlib import pyplot as plt
import matplotlib

matplotlib.rc("lines", linewidth=2)
# matplotlib.rc("figure", figsize=(16,6))

from cvxpower import Net, Group, Storage, Generator, Device, Terminal
import cvxpy as cvx
import pandas as pd
import numpy as np

class Grid(Generator):
    def __init__(self, rate=None, **kwargs):
        rate = rate[None]
        super(Grid, self).__init__(alpha=np.zeros(rate.shape), beta=rate, **kwargs)


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

def energy_rate(index):
    retval = np.zeros(len(index))
    # PG&E Proposed CEV rate structure
    retval[(index.hour >= 0) & (index.hour < 9)] = 0.11
    retval[(index.hour >= 9) & (index.hour < 14)] = 0.09
    retval[(index.hour >= 14) & (index.hour < 16)] = 0.11
    retval[(index.hour >= 16) & (index.hour < 22)] = 0.30
    retval[(index.hour >= 22) & (index.hour < 24)] = 0.11
    return retval


def charge_max(index, departure_time, limit_kw):
    retval = np.zeros(len(index))
    retval[index < departure_time] = limit_kw
    return retval


start = pd.Timestamp("2020-03-09 08:00")
index = pd.date_range(start, start + pd.DateOffset(hours=12), freq="15min")[:-1]

vehicles = [
    EV(
        name="Alice",
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 17:00"), limit_kw=6.6
        ),
        energy_init=23.0,
        energy_final=75.0,
    ),
    EV(
        name="Bob",
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 17:45"), limit_kw=6.6
        ),
        energy_init=20.0,
        energy_final=50.0,
    ),
    EV(
        name="Carol",
        charge_max=charge_max(
            index, pd.Timestamp("2020-03-09 11:00"), limit_kw=3.3
        ),
        energy_init=0.0,
        energy_final=8.8,
    ),
]
grid = Grid(energy_rate(index))
transformer = Transformer(power_max=10)

net_v = Net([v.terminals[0] for v in vehicles] + [transformer.terminals[0]], name="EVSE")
net_g = Net([grid.terminals[0], transformer.terminals[1]], name="Grid")
network = Group(vehicles + [grid, transformer], [net_v, net_g])
results = network.optimize(time_horizon=len(index), verbose=True, solver="ECOS")
print(results)

power = np.stack([v.terminals[0].power_var.value[:, 0] for v in vehicles], axis=1)
names = [v.name for v in vehicles]
power = pd.DataFrame(power, index=index, columns=names)
np.maximum(power, 0.).plot.area()

avg_price = np.sum((power.sum(axis=1) * energy_rate(index))) / np.sum(power.sum(axis=1))
print("Average price: $%.04f / kWh" % avg_price)
