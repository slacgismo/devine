# Split data between session and interval and then select each individual column to build the dataframe for creating the statistics.

# import boto3
import pandas as pd
import pickle
from datetime import datetime, date, timedelta
from matplotlib import pyplot as plt
import matplotlib
import numpy as np

def hour2min(series, minutes=15):
    retval = []
    for i in series:
        retval.append(int(np.floor((i.hour * 60 + i.minute) * 60 + i.second) / 60 / minutes))
    return retval

def hour2min15(data):
    retval = []
    for i in data:
        temp = i.split(':')
        retval.append(int(np.floor(((int(temp[0])*3600 + int(temp[1])*60 + int(temp[0]))/900))))
    return retval


file_path = 's3://devine.fielddemo.data/Google/clean/MTV-46-2020 Session-Details-Meter-with-Summary.csv'
print('Reading file')
data1 = pd.read_csv(file_path)
# file_name = '~/Downloads/SLAC-Session-Details-Meter-with-Summary-2018.csv'
# file_name = '~/Downloads/MTV-CRIT-2018-Session-Details-Meter-with-Summary.csv'
# file_name = '~/Downloads/MTV-46 2020 Session-Details-Meter-with-Summary.csv'

# Saving distributions
title = 'MTV 2020 '
folder = 'Google/MTV/monthly'
# title = 'SLAC 2018 '
# folder = 'SLAC/monthly'

# print('Reading file')
# *****
# data1 = pd.read_csv(file_name, low_memory=False)
cols_interval = data1.columns[0:15]
cols_session = data1.columns[16:]

data2 = data1.copy()
data2['Total Duration 15min'] = hour2min15(data2['Total Duration (hh:mm:ss)'])
data2['Charging Time 15min'] = hour2min15(data2['Charging Time (hh:mm:ss)'])
data2['End Time 15min'] = np.floor(data2['start_seconds']/900 + data2['Total Duration 15min'])
data2['Start Time 15min'] = np.floor(data2['start_seconds']/900)

start_inds = np.arange(0,96)*0.25

# Statistics - overall data:
tot_sessions = len(data2)
print('Total # of sessions: ', tot_sessions)


def distribution(df_column, dict_plot_label=None, save_fig=False, folder='Google/CRIT'):
    if dict_plot_label is None:
        dict_plot_label = {'xlabel': 'Hour', 'ylabel': 'Frequency', 'title': 'Distribution'}
    start_inds = np.arange(0, 96) * 0.25
    # (unique, counts) = np.unique(df_column, return_counts=True)
    (unique, counts) = np.unique(df_column / 4, return_counts=True)
    freq = np.zeros(96,)
    for ix, i in enumerate(start_inds):
        for idx, j in enumerate(unique):
            if j == i:
                freq[ix] = counts[idx]
    fig, ax = plt.subplots(figsize = (10,4))
    ax.bar(start_inds, freq, alpha=1, edgecolor='k', width=0.2)
    ax.set_xticks(np.arange(0,24,2))
    ax.set_xlabel(dict_plot_label['xlabel'])
    ax.set_ylabel(dict_plot_label['ylabel'])
    ax.set_title(dict_plot_label['title'])
    if save_fig:
        plt.savefig('DataAnalysis/' + folder + '/' + dict_plot_label['title'] + '.png', bbox_inches='tight')
    # plt.show()

# Stats List:
stats_dict = {'Charging Duration': 'Charging Time 15min', 'Arrival': 'Start Time 15min', 'Departure': 'End Time 15min', 'Session Duration': 'Total Duration 15min', 'Energy': 'Energy (kWh)'}

# Statistics - all weekdays in every month:
month = np.arange(1,13)
month_list = []
for i in month:
    month_list.append(data2[data2['start_month'] == i])
# df_weekday = data2[(data2['start_day']>= 0) & (data2['start_day'] < 5)]
# for i in month:
#     month_list.append(df_weekday[df_weekday['start_month'] == i])

########################
# Saving Distributions
for ix, i in enumerate(month_list):
    for key in stats_dict:
        if key == 'Energy':
            i.hist(column='Energy (kWh)', bins=20, rwidth=0.9)
            plt.xticks(np.arange(0, 70, 5))
            plt.xlabel('Energy (kWh)')
            plt.ylabel('Frequency')
            plt.title(title+'Energy (kWh) - Month' + str(ix+1))
            # plt.savefig('DataAnalysis/' + folder + '/' + title+'Energy - Month' + str(ix+1) + '.png', bbox_inches='tight')
            plt.show()
        else:
            distribution(i[stats_dict[key]], {'xlabel': 'Hour', 'ylabel': 'Frequency',
                                                    'title': title + key + ' - Month ' + str(ix + 1)},
                         save_fig=False, folder=folder)
        # distribution(i['Charging Time 15min'], {'xlabel': 'Hour', 'ylabel': 'Frequency', 'title': title + 'Charging Duration - Month ' + str(ix+1)}, save_fig=True, folder=folder)
print('Sessions per month:')
for i in month_list:
    print(len(i))
########################
#
# # Statistics - single weekday in every month:
# # weekday_arr = np.arange(0,5) # -> [Mon, Tue, Wed, Thu, Fri]
# # for ix, i in enumerate(month_list):
# #     for d in weekday_arr:
# #         day_month = i[i['Daily Start Time'] == d]
# #         distribution(day_month[])
#
#
# # energy
# for ix, i in enumerate(month_list):
#     i.hist(column='Energy (kWh)', bins=20, rwidth=0.9)
#     plt.xticks(np.arange(0, 70, 5))
#     plt.xlabel('Energy (kWh)')
#     plt.ylabel('Frequency')
#     plt.title(title+'Energy (kWh) - Month' + str(ix+1))
#     plt.savefig('DataAnalysis/' + folder + '/' + title+'Energy - Month' + str(ix+1) + '.png', bbox_inches='tight')
#     plt.show()

# Statistics - weekday:




# rel_fields = ['EVSE ID','User Id','Org Name', 'Start Time', 'End Time', 'Total Duration (hh:mm:ss)', 'Charging Time (hh:mm:ss)', 'Energy (kWh)']
# data2 = data2[rel_fields]
# data2 = data2.dropna()
# data2 = data2.reset_index()
# data2['Start Time'] = pd.to_datetime(data2['Start Time'])
# data2['End Time'] = pd.to_datetime(data2['End Time'])
# data2['Total Duration (hh:mm:ss)'] = pd.to_datetime(data2['Total Duration (hh:mm:ss)'])
# data2['Charging Time (hh:mm:ss)'] = pd.to_datetime(data2['Charging Time (hh:mm:ss)'])
# data2['Start Date'] = data2['Start Time'].dt.date
# data2['End Date'] = data2['End Time'].dt.date
# data2['Month Start Time'] = data2['Start Time'].dt.month
# data2['Month End Time'] = data2['End Time'].dt.month
# data2['Daily Start Time'] = data2['Start Time'].dt.weekday
# data2['Daily End Time'] = data2['End Time'].dt.weekday
# data2['Start 15min'] = hour2min(data2['Start Time'].dt.floor('15T').dt.time)
# data2['End 15min'] = hour2min(data2['End Time'].dt.floor('15T').dt.time)
# data2['Total Duration 15min'] = hour2min(data2['Total Duration (hh:mm:ss)'].dt.floor('15T'))
# data2['Charging Time 15min'] = hour2min(data2['Charging Time (hh:mm:ss)'].dt.floor('15T'))



# distribution arrival time
# (unique, counts) = np.unique(data2['Start 15min']/4, return_counts=True)
# freq = np.zeros(96,)
# for ix, i in enumerate(start_inds):
#     for idx, j in enumerate(unique):
#         if j == i:
#             freq[ix] = counts[idx]
# fig, ax = plt.subplots(figsize = (10,4))
# ax.bar(start_inds, freq, alpha=1, edgecolor='k', width=0.2)
# ax.set_xticks(np.arange(0,24,2))
# ax.set_xlabel('Hour')
# ax.set_ylabel('Frequency')
# ax.set_title('SLAC - 2018 - Arrival')
# plt.show()

# distribution departure time
# (unique, counts) = np.unique(data2['End 15min']/4, return_counts=True)
# freq = np.zeros(96,)
# for ix, i in enumerate(start_inds):
#     for idx, j in enumerate(unique):
#         if j == i:
#             freq[ix] = counts[idx]
#
# fig, ax = plt.subplots(figsize = (10,4))
# ax.bar(start_inds, freq, alpha=1, edgecolor='k', width=0.2)
# ax.set_xticks(np.arange(0,24,2))
# ax.set_xlabel('Hour')
# ax.set_ylabel('Frequency')
# ax.set_title('SLAC - 2018 - Departure')
# plt.show()

# energy
# dist_energy
# data2.hist(column='Energy (kWh)',bins=20,rwidth=0.9)
# plt.xticks(np.arange(0, 70, 5))
# plt.show()

# dist_session_dur
# (unique, counts) = np.unique(data2['Total Duration 15min']/4, return_counts=True)
# freq = np.zeros(96,)
# for ix, i in enumerate(start_inds):
#     for idx, j in enumerate(unique):
#         if j == i:
#             freq[ix] = counts[idx]
#
# fig, ax = plt.subplots(figsize = (10,4))
# ax.bar(start_inds, freq, alpha=1, edgecolor='k', width=0.2)
# ax.set_xticks(np.arange(0,24,2))
# ax.set_xlabel('Hour')
# ax.set_ylabel('Frequency')
# ax.set_title('SLAC - 2018 - Session Duration')
# plt.show()

# dist_charg_dur
# (unique, counts) = np.unique(data2['Charging Time 15min']/4, return_counts=True)
# freq = np.zeros(96,)
# for ix, i in enumerate(start_inds):
#     for idx, j in enumerate(unique):
#         if j == i:
#             freq[ix] = counts[idx]
#
# fig, ax = plt.subplots(figsize = (10,4))
# ax.bar(start_inds, freq, alpha=1, edgecolor='k', width=0.2)
# ax.set_xticks(np.arange(0,24,2))
# ax.set_xlabel('Hour')
# ax.set_ylabel('Frequency')
# ax.set_title('SLAC - 2018 - Charging Duration')
# plt.show()




# df.groupby(df["date"].dt.month).count().plot(kind="bar")
# data2 = pd.read_csv(file_name)
# rel_fields = ['EVSE ID','User Id','Org Name', 'Start Time', 'End Time', 'Total Duration (hh:mm:ss)', 'Charging Time (hh:mm:ss)', 'Energy (kWh)', 'Peak Power (AC kW)']
# data2 = data2[rel_fields]
# data2['Peak Power (AC kW)'].fillna(method='bfill', limit=1, inplace=True)
# data2['Peak Power (AC kW)'].fillna(method='ffill', limit=1, inplace=True)
#
# subset = data2[['User Id', 'Start Time', 'Peak Power (AC kW)']]
# subset['Start Time'].fillna(method='ffill', inplace=True)

# This should go to the other file with the
# df = data2.sort_values(by=['User Id'])
# df1 = df.reset_index()
# df1.drop(['index'])


