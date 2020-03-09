import s3fs, boto3
import pandas as pd
import requests, json, time, datetime, schedule
import config
from io import StringIO
import boto3
s3_resource = boto3.resource('s3')

username = config.username
password = config.password
data_login = json.dumps({"username":username, "password":password})
headers = {'cache-control': 'no-cache', 'content-type': 'application/json',}

url_login = 'https://slac.powerflex.com:9443/login'
resp_login = requests.post(url_login, headers=headers, data=data_login)
url_archive = 'https://archive.powerflex.com/login'
resp_archive = requests.post(url_archive, headers=headers, data=data_login)

token_meas = json.loads(resp_login.text)['access_token']
auth_token_meas = 'Bearer '+ token_meas
headers_meas = {'cache-control': 'no-cache', 'content-type': 'application/json',
                'Authorization':auth_token_meas,}

# url for interval data
url_measurement = 'https://slac.powerflex.com:9443/get_measurement_data'

token_arch = json.loads(resp_archive.text)['access_token']
auth_token_arch = 'Bearer '+ token_arch
headers = {'cache-control': 'no-cache', 'content-type': 'application/json',
           'Authorization':auth_token_arch,}

# urls for session data from two different sites
url_arch1 = 'https://archive.powerflex.com/get_csh/0032/01'
url_arch2 = 'https://archive.powerflex.com/get_csh/0032/02'



def interval_data_collection(start,end):
    data_meas = json.dumps({"measurement":"ct_response", "time_filter":[start,end]})
    r = requests.post(url_measurement, headers=headers_meas, data=data_meas)
    data = json.loads(r.text)
    return(pd.DataFrame(data=data['data']['results'][0]['series'][0]['values'],
                     columns=data['data']['results'][0]['series'][0]['columns']))



def session_data_collection(start, end):
    # 2 different charging stations
    data_meas = json.dumps({"measurement":"ct_response", "time_filter":[start,end]})
    data_in = json.dumps({"startTime":start, "stopTime":end, "filterBy":"sessionStopTime", "anonymize":True})
    r1 = requests.post(url_arch1, headers=headers, data=data_in)
    r2 = requests.post(url_arch2, headers=headers, data=data_in)
    data1 = json.loads(r1.text)
    df1 = pd.DataFrame(data1['sessions'])
    data2 = json.loads(r2.text)
    df2 = pd.DataFrame(data2['sessions'])
    return df1, df2


def main():

    # interval data collection - previous day's data
    d_int = datetime.datetime.today() - datetime.timedelta(days=1)
    month_int = d_int.month
    day_int = d_int.day
    year_int = d_int.year

    # session data collection - data from 10 days ago
    d_ses = datetime.datetime.today() - datetime.timedelta(days=10)
    month_ses = d_ses.month
    day_ses = d_ses.day
    year_ses = d_ses.year

    df_int = pd.DataFrame()
    df_ses_1 = pd.DataFrame()
    df_ses_2 = pd.DataFrame()

# data collected in 2 steps - works more consistently
# larger requests to the powerflex API may fail
    hour_sets = [[0, 11],[12, 23]]

    for hour_set in hour_sets:
        start_int = int(datetime.datetime(2020, int(month_int), int(day_int), hour_set[0], 0).timestamp())
        end_int = int(datetime.datetime(2020, int(month_int), int(day_int), hour_set[1], 0).timestamp())
        df_int = df_int.append(interval_data_collection(start_int,end_int))

        start_ses = int(datetime.datetime(2020, int(month_ses), int(day_ses), hour_set[0], 0).timestamp())
        end_ses = int(datetime.datetime(2020, int(month_ses), int(day_ses), hour_set[1], 0).timestamp())
        df1, df2 = session_data_collection(start_ses,end_ses)
        df_ses_1 = df_ses_1.append(df1)
        df_ses_2 = df_ses_2.append(df2)


    csv_buffer = StringIO()
    pd.DataFrame(data=df_int).to_csv(csv_buffer)
    s3_resource.Object('devine.powerflex.data', 'raw/interval/'+ str(year_int) + '-'
                        + str(month_int) + '-' + str(day_int) + 'df_int.csv').put(Body=csv_buffer.getvalue())


    csv_buffer = StringIO()
    pd.DataFrame(data=df_ses_1).to_csv(csv_buffer)
    s3_resource.Object('devine.powerflex.data', 'raw/session/'+ str(year_ses) + '-'
                        + str(month_ses) + '-' + str(day_ses) + 'df_ses_1.csv').put(Body=csv_buffer.getvalue())


    csv_buffer = StringIO()
    pd.DataFrame(data=df_ses_2).to_csv(csv_buffer)
    s3_resource.Object('devine.powerflex.data', 'raw/session/'+ str(year_ses) + '-'
                    + str(month_ses) + '-' + str(day_ses) + 'df_ses_2.csv').put(Body=csv_buffer.getvalue())

# schedule.every().day.at("04:00").do(main)

if __name__ == '__main__':
    main()

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
