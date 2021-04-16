from datetime import datetime
import re
import pandas as pd
import numpy as np

data = pd.read_csv("Plymouth 2019 Session-Details-Meter-with-Summary.csv", low_memory=False)

n_stations = data['EVSE ID'].unique()
print("The number of unique stations is: ", len(n_stations))

dc_port = data[data['Port Type'] == 'DC Fast']
n_dcfc = dc_port['EVSE ID'].unique()

print("Total number of L2 ports is {} and DCFC is {}".format((len(n_stations)-len(n_dcfc))*2, len(n_dcfc)))

###### Number of sessions per station port ######
# Return dict with key being station ID and value is  tuple of (total number of sessions in station,
# number of sess port 1 and number of sess port 2)
sessions_dict = dict.fromkeys(n_stations)
for i in n_stations:
    port1 = 0
    port2 = 0
    station = data[data['EVSE ID'] == i]
    sessions = station['Plug In Event Id'].unique()
    for e in sessions:
        plug_event = station[station['Plug In Event Id'] == e]
        if int(plug_event['Port'].unique()) == 1:
            port1 += 1
        elif int(plug_event['Port'].unique()) == 2:
            port2 += 1
        else:
            print('Port cant be found for station {} and plug in event {}'.format(i, e))
    sessions_dict[i] = (len(sessions), port1, port2)

###### User Frequency ######
users = data['User Id'].unique()
users_group = data.groupby('User Id')
users_dict = dict.fromkeys(users)
for u in users:
    group = users_group.get_group(u)
    total_sessions = len(group['Plug In Event Id'].unique())
    users_dict[u] = total_sessions

###### Map of EVSE ID to Station Name ######
id2station = data.groupby(['EVSE ID', 'Station Name']).size().reset_index()
id2station_list = id2station[['EVSE ID', 'Station Name']].values.tolist()

station_id_2 = []
station_goo_id_2 = []
pattern = re.compile("MTV-1625-2")
for i in id2station_list:
    if pattern.search(i[1]):
        station_id_2.append(i[0])
        station_goo_id_2.append(i[1][-2:])

station_id_3 = []
station_goo_id_3 = []
pattern = re.compile("MTV-1625-3")
for i in id2station_list:
    if pattern.search(i[1]):
        station_id_3.append(i[0])
        station_goo_id_3.append(i[1][-2:])

station_goo_id_2 = ['GOOGLE / MTV-1625-2-' + s for s in station_goo_id_2]
station_goo_id_3 = ['GOOGLE / MTV-1625-3-' + s for s in station_goo_id_3]
zipObj2 = zip(station_id_2, station_goo_id_2)
google_st = dict(zipObj2)
zipObj3 = zip(station_id_3, station_goo_id_3)
google_3_st = dict(zipObj3)

google_st.update(google_3_st)

###### Create GLD dataframe ######
df_gld = data[['EVSE ID', 'User Id', 'Plug In Event Id', 'Power Start Time', 'Power End Time', 'Peak Power (AC kW)', 'Rolling Avg. Power (AC kW)', 'Energy Consumed (AC kWh)', 'Port']]

###### Creating datetime column for GLD simulator ######
df_gld = df_gld.dropna()
df_gld.reset_index(drop=True)
df_gld['Datetime'] = pd.to_datetime(df_gld['Power Start Time'])
# df_gld['Datetime'] = df_gld['Datetime'].astype('datetime64[ns]')
df_gld['Day'] = df_gld['Datetime'].dt.day
df_gld['Month'] = df_gld['Datetime'].dt.month
df_gld['Year'] = df_gld['Datetime'].dt.year

###### Grouping y year -> month -> day ######
groupDate_gld = df_gld.groupby(['Year', 'Month', 'Day'])

###### Selecting a day to feed simulation ######
gld_input = groupDate_gld.get_group((2019, 7, 29))

###### Adding station full name to feed simulation ######
evse = gld_input['EVSE ID']
st_name = []
for i in evse:
   st_name.append(google_st[i] + '-')

gld_input['st_name'] = st_name
gld_input['gld_station_name'] = gld_input['st_name'] + gld_input['Port'].astype(str)
gld_input.drop('st_name', axis=1, inplace=True)
gld_input.drop('Plug In Event Id', axis=1, inplace=True)

###### Create mapping between station names and phase ######
# Phases mapping are hardcoded for Plymouth site
phases = ['BC', 'AB', 'CA', 'BC', 'AB', 'CA', 'BC', 'AB', 'AB', 'CA', 'BC', 'AB', 'CA', 'BC', 'AB', 'CA', 'BC', 'AB', 'AB', 'CA', 'BC', 'AB', 'CA', 'BC', 'AB', 'CA', 'BC', 'AB', 'CA', 'BC']
phases_total = phases + phases
station_goo = sorted(station_goo_id_2) + sorted(station_goo_id_3)
station_goo_ports = []
for s in station_goo:
    station_goo_ports.append(s + '-1')
    station_goo_ports.append(s + '-2')

port_phases = dict(zip(station_goo_ports, phases_total))




