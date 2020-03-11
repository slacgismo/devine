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


def date_generator(delta):
    d = datetime.datetime.today() - datetime.timedelta(days=delta)
    month = d.month
    day = d.day
    year = d.year
    return (month, day, year)


def save_to_s3(df, type, delta):
    # delta determines how many days ago
    month, day, year = date_generator(delta)

    s3_resource = boto3.resource("s3")
    csv_buffer = StringIO()
    pd.DataFrame(data=df).to_csv(csv_buffer)
    s3_resource.Object("devine.powerflex.data",
                       f"raw/{type}/{year}-{month}-{day}df_{type}.csv").put(
                       Body=csv_buffer.getvalue())


def timestamp_generator(delta, hour_start, hour_end):
    # delta determines how many days ago
    month, day, year = date_generator(delta)

    start = int(datetime.datetime(year, int(month), int(day), hour_start, 0).timestamp())
    end = int(datetime.datetime(year, int(month), int(day), hour_end, 0).timestamp())
    return start, end


def main(username, password):
    # headers_meas and headers used for calling data_collection functions
    headers_meas, headers = api_login(username, password)

    df_int = pd.DataFrame()
    df_ses_1 = pd.DataFrame()
    df_ses_2 = pd.DataFrame()

    # data collected in 2 steps - works more consistently
    # larger requests to the powerflex API may fail
    hour_sets = [[0, 11], [12, 23]]

    for hour_set in hour_sets:
        # interval data collection - previous days data
        start_int, end_int = timestamp_generator(1, hour_set[0], hour_set[1])
        df_int = df_int.append(interval_data_collection(start_int, end_int,
                               headers_meas))

        # session data collection - data from 10 days ago
        # data is updated in 7 day intervals on powerflex's side
        start_ses, end_ses = timestamp_generator(10, hour_set[0], hour_set[1])
        df1, df2 = session_data_collection(start_ses, end_ses, headers)

        df_ses_1 = df_ses_1.append(df1)
        df_ses_2 = df_ses_2.append(df2)

    save_to_s3(df_int, "interval", 1)
    save_to_s3(df_ses_1, "session", 10)
    save_to_s3(df_ses_2, "session", 10)


if __name__ == "__main__":
    username = str(sys.argv[1])
    password = str(sys.argv[2])
    main(username, password)
