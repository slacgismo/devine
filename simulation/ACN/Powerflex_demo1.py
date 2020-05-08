#!/usr/bin/env python
# coding: utf-8

# # Import Packages

# In[30]:


import pytz
from datetime import datetime
import matplotlib.pyplot as plt
from acnportal import acnsim
from acnportal import acndata
from acnportal import algorithms
import pandas as pd


# # Import Dataset

# In[31]:


df = pd.read_csv('2020-2-28df_session.csv')

# Convert time related columns to datetime objects.
df['evConnectionTime'] = df['evConnectionTime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))
df['sessionStopTime'] = df['sessionStopTime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))
df.sort_values(by=['evConnectionTime'])


# # Experiment Parameters

# In[32]:


# Timezone of the ACN we are using.
timezone = pytz.timezone('America/Los_Angeles')

# Start and End times of the simulation.
start = datetime(2020, 2, 28, 14)
end = datetime(2020, 2, 29)

# How long each time discrete time interval in the simulation should be.
period = 5  # minutes

# Voltage of the network.
voltage = 220  # volts

phase_angle = 30 # degrees

# Default maximum charging rate for each EV battery.
default_max_power = 32 * voltage / 1000 # kW


# # Charging Network Setup

# In[34]:


station_id_list = df['spaceId'].unique() # list of all unique spaceIDs in the dataset
cn = acnsim.network.ChargingNetwork()
for i in df.index:
    cur_EVSE = acnsim.models.evse.EVSE(df['spaceId'][i], max_rate=80, min_rate=0) 
    cn.register_evse(cur_EVSE,voltage,phase_angle)


# # Events

# In[35]:


# function for creating two events (plugin and unplug) for each charging session
def create_event(event_data):
    # Convert arrival and departure times to number of periods since simulation started.
    arrival = int((event_data['evConnectionTime'] - start).seconds/60/period)
    departure = int((event_data['sessionStopTime'] - start).seconds/60/period)
    
    # Requested energy in kWh
    requested_energy = event_data['milesNeeded']*event_data['WhPerMile']/1000
    
    space_id = event_data['spaceId']
    session_id = event_data['chargeSessionId']
    
    # assume that the battery is empty and the capacity is the requested energy
    default_capacity = requested_energy
    default_init_charge = 0
    battery = acnsim.models.battery.Battery(default_capacity, default_init_charge, default_max_power)
    
    # create EV object
    ev = acnsim.models.ev.EV(arrival, departure, requested_energy, space_id, session_id, battery, estimated_departure=None)
    
    #create plugin and unplug events using the EV object
    plugin_event = acnsim.events.PluginEvent(arrival,ev)
    unplug_event = acnsim.events.UnplugEvent(departure, space_id, session_id)
    return (plugin_event, unplug_event)

# loop over the dataset and create a queue of plugin and unplug event for each session
events = acnsim.events.EventQueue()
for index, row in df.iterrows(): 
    events.add_events(create_event(row))


# # Scheduling Algorithm

# In[36]:


sch_uncontrolled = algorithms.UncontrolledCharging()


# # Simulation

# In[37]:


sim = acnsim.Simulator(cn, sch_uncontrolled, events, start, period=period, verbose=False)
sim.run()


# # Analysis

# In[38]:


def analyze_simulation(sim):
    total_energy_prop = acnsim.proportion_of_energy_delivered(sim)
    print('Proportion of requested energy delivered: {0}'.format(total_energy_prop))
    print('Peak aggregate current: {0} A'.format(sim.peak))
    # Plotting aggregate current
    agg_current = acnsim.aggregate_current(sim)
    plt.plot(agg_current)
    plt.xlabel('Time (periods)')
    plt.ylabel('Current (A)')
    plt.title('Total Aggregate Current')
    plt.savefig('output.png')
    plt.show()
analyze_simulation(sim)

