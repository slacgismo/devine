import boto3
import pandas as pd
import pickle
from datetime import datetime, date

file_path = 's3://devine.fielddemo.data/SLAC/raw/SLAC-Session-Details-Meter-with-Summary-2018.csv'
file_name = 'SLAC-Session-Details-Meter-with-Summary-2018.csv'

print('Reading file')
# *****
data2 = pd.read_csv(file_path)
rel_fields = ['EVSE ID','User Id','Org Name', 'Start Time', 'End Time', 'Total Duration (hh:mm:ss)', 'Charging Time (hh:mm:ss)', 'Energy (kWh)', 'Peak Power (AC kW)']
data2 = data2[rel_fields]
data2['Peak Power (AC kW)'].fillna(method='bfill', limit=1, inplace=True)
data2['Peak Power (AC kW)'].fillna(method='ffill', limit=1, inplace=True)

subset = data2[['User Id', 'Start Time', 'Peak Power (AC kW)']]
subset['Start Time'].fillna(method='ffill', inplace=True)

# This should go to the other file with the
# df = data2.sort_values(by=['User Id'])
# df1 = df.reset_index()
# df1.drop(['index'])
