import boto3
import pandas as pd
import pickle
from datetime import datetime, date

file_path = 's3://devine.fielddemo.data/Google/raw/MTV-CRIT-2018-Session-Details-Meter-with-Summary.csv'
file_name = 'MTV-CRIT-2018-Session-Details-Meter-with-Summary'

print('Reading file')
data1 = pd.read_csv(file_path)
# data1 = pd.read_csv('MTV-CRIT-2020-Session-Details-Meter-with-Summary.csv')
print('--- Preprocessing ---')
relevant_fields = ['EVSE ID','User Id','Org Name', 'Start Time', 'End Time', 'Total Duration (hh:mm:ss)',
                   'Charging Time (hh:mm:ss)', 'Energy (kWh)']
data1 = data1[relevant_fields]
data1 = data1.dropna()

print('Number of sessions: ', len(data1))
print('----------')

print('--- Cleaning ---')
print('Data set ranges from ', pd.to_datetime(data1['Start Time']).min(), ' to ',
      pd.to_datetime(data1['Start Time']).max())

cleaning_dict = {'Original Num Sessions': len(data1)}


def convert_to_seconds(x):
    times = x.split(':')
    return (60*int(times[0])+60*int(times[1]))+int(times[2])


def remove_less_than(data, col, threshold):
    if col == 'Total Duration (hh:mm:ss)' or col == 'Charging Time (hh:mm:ss)':
        num_dropped = sum(data[col].apply(convert_to_seconds) < threshold)
        print("removing {} occurences of {} of less than {}".format(num_dropped, col, threshold))
        return data[data[col].apply(convert_to_seconds) >= threshold], num_dropped
    else:
        num_dropped = sum(data[col] < threshold)
        print("removing {} occurences of {} of less than {}".format(num_dropped, col, threshold))
        return data[data[col] >= threshold], num_dropped


def remove_greater_than(data, col, threshold):
    num_dropped = sum(data[col] > threshold)
    print("removing {} occurences of {} of greater than {}".format(num_dropped, col, threshold))
    return data[data[col] <= threshold], num_dropped


data1, num_dropped = remove_less_than(data1, 'Energy (kWh)', 0.1)
cleaning_dict['Energy < 0.1'] = num_dropped

data1, num_dropped = remove_less_than(data1, 'Total Duration (hh:mm:ss)', 60)
cleaning_dict['Session Time < 60s'] = num_dropped

data1, num_dropped = remove_greater_than(data1, 'Energy (kWh)', 100)
cleaning_dict['Energy > 100'] = num_dropped


def to_datetime(x):
    return datetime.strptime(x, "%m/%d/%y %H:%M")


def to_seconds(x):
    """seconds in current day since midnight"""
    return 60 * 60 * x.hour + 60 * x.minute + x.second


def to_year(x):
    return x.year


def to_month(x):
    return x.month


def to_day(x):
    """day of year, [1, 366]"""
    return x.timetuple().tm_yday


def to_weekday(x):
    """weekday, [0, 6]"""
    return x.weekday()


def apply_transforms(data, col, transforms, names, drop_col=False):
    """apply multiple transforms"""
    for n, t in zip(names, transforms):
        print("applying transfrom {} to {}".format(n, col))
        data[n] = data[col].apply(t)
    if drop_col:
        print("dropping {}".format(col))
        data = data.drop(columns=[col])
    return data


def transform_start_datetimes(data):
    col = 'Start Time'

    l1 = len(data)
    # remove sessions where timestamp is not a string
    data = data[data[col].apply(lambda x: type(x)) == type("")]
    l2 = len(data)
    n_dropped1 = l1 - l2
    print("removed {} sessions where timestamp was not a string".format(n_dropped1))

    transforms = [to_datetime, to_seconds, to_year, to_month, to_day, to_weekday]
    names = ["datetime", "seconds", "year", "month", "day", "weekday"]
    names = ["start_{}".format(x) for x in names]

    # create datetime object from string
    data = apply_transforms(data, col, [transforms[0]], [names[0]], drop_col=False)
    # all other transfroms are applied to datetime object
    data = apply_transforms(data, names[0], transforms[1:], names[1:], drop_col=False)

    return data, n_dropped1


data1, n_dropped1 = transform_start_datetimes(data1)
cleaning_dict['Start Time Format'] = n_dropped1

print('----------------')
print('Total loss to cleaning: ', (
            cleaning_dict['Energy < 0.1'] + cleaning_dict['Energy > 100'] + cleaning_dict['Session Time < 60s'] +
            cleaning_dict['Start Time Format']))

data1.reset_index(drop=True, inplace=True)
data1.to_csv('s3://devine.fielddemo.data/Google/clean/'+file_name, index=False)
