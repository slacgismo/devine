import s3fs
import boto3
import pandas as pd
import requests
import json
import time
import datetime
import sys
from io import StringIO

# url for interval data
URL_MEASUREMENT = "https://slac.powerflex.com:9443/get_measurement_data"

# urls for session data from two different sites
URL_ARCH1 = "https://archive.powerflex.com/get_csh/0032/01"
URL_ARCH2 = "https://archive.powerflex.com/get_csh/0032/02"

URL_LOGIN = "https://slac.powerflex.com:9443/login"
URL_ARCHIVE = "https://archive.powerflex.com/login"

def login_request(r):
    token = r.json()["access_token"]
    auth_token = f"Bearer {token}"
    headers = {"cache-control": "no-cache", "content-type": "application/json",
               "Authorization": auth_token}
    return(headers)


def data_request(url, headers, data):
    r = requests.post(url, headers=headers, data=data)
    return(r.json())


def api_login(username, password):
    data_login = json.dumps({"username": username, "password": password})
    headers = {"cache-control": "no-cache", "content-type": "application/json"}
    r_login = requests.post(URL_LOGIN, headers=headers, data=data_login)
    r_archive = requests.post(URL_ARCHIVE, headers=headers, data=data_login)
    return (login_request(r_login), login_request(r_archive))


def interval_data_collection(start, end, headers):
    data = json.dumps({"measurement": "ct_response",
                       "time_filter": [start, end]})
    data = data_request(URL_MEASUREMENT, headers, data)
    df = pd.DataFrame(data=data["data"]["results"][0]["series"][0]["values"],
                      columns=data["data"]["results"][0]["series"][0]["columns"])
    return(df)


def session_data_collection(start, end, headers):
    data = json.dumps({"startTime": start, "stopTime": end, "filterBy":
                          "sessionStopTime", "anonymize": True})
    df1 = pd.DataFrame(data_request(URL_ARCH1, headers, data)["sessions"])
    df2 = pd.DataFrame(data_request(URL_ARCH2, headers, data)["sessions"])
    return df1, df2


def save_to_s3(df, type, year, month, day):
    s3_resource = boto3.resource("s3")
    csv_buffer = StringIO()
    pd.DataFrame(data=df).to_csv(csv_buffer)
    s3_resource.Object("devine.powerflex.data",
                       f"raw/{type}/{year}-{month}-{day}df_{type}.csv").put(
                       Body=csv_buffer.getvalue())


def main(username, password):
    # headers_meas and headers used for calling data_collection functions
    headers_meas, headers = api_login(username, password)
    # interval data collection - previous days data
    d_int = datetime.datetime.today() - datetime.timedelta(days=1)
    month_int = d_int.month
    day_int = d_int.day
    year_int = d_int.year

    # session data collection - data from 10 days ago
    # data is updated in 7 day intervals on powerflex's side
    d_ses = datetime.datetime.today() - datetime.timedelta(days=10)
    month_ses = d_ses.month
    day_ses = d_ses.day
    year_ses = d_ses.year

    df_int = pd.DataFrame()
    df_ses_1 = pd.DataFrame()
    df_ses_2 = pd.DataFrame()

    # data collected in 2 steps - works more consistently
    # larger requests to the powerflex API may fail
    hour_sets = [[0, 11], [12, 23]]

    for hour_set in hour_sets:
        start_int = int(datetime.datetime(2020, int(month_int), int(day_int),
                        hour_set[0], 0).timestamp())
        end_int = int(datetime.datetime(2020, int(month_int), int(day_int),
                      hour_set[1], 0).timestamp())
        df_int = df_int.append(interval_data_collection(start_int, end_int,
                               headers_meas))

        start_ses = int(datetime.datetime(2020, int(month_ses), int(day_ses),
                        hour_set[0], 0).timestamp())
        end_ses = int(datetime.datetime(2020, int(month_ses), int(day_ses),
                      hour_set[1], 0).timestamp())
        df1, df2 = session_data_collection(start_ses, end_ses, headers)

        df_ses_1 = df_ses_1.append(df1)
        df_ses_2 = df_ses_2.append(df2)

    save_to_s3(df_int, "interval", year_int, month_int, day_int)
    save_to_s3(df_ses_1, "session", year_ses, month_ses, day_ses)
    save_to_s3(df_ses_2, "session", year_ses, month_ses, day_ses)


if __name__ == "__main__":
    username = str(sys.argv[1])
    password = str(sys.argv[2])
    main(username, password)
