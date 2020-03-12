import sys
import s3fs
import json
import time
import boto3
import requests
import datetime
import pandas as pd
from io import StringIO

# specify the offset, in days, for the data request of interval and session data
INTERVAL_DAY_OFFSET = 1
SESSION_DAY_OFFSET = 10

# start and end times, in hours and zero based, so we can split the size of the data request
AM_START = 0
AM_END = 11
PM_START = 12
PM_END = 23

# S3 Bucket in the SLAC-Gismo account where we are saving all the requested data
S3_BUCKET = "devine.powerflex.data"

# URLs required to authenticate and query for data
URLS = {
    "SLAC": {
        "LOGIN": "https://slac.powerflex.com:9443/login",
        "MEASUREMENT": "https://slac.powerflex.com:9443/get_measurement_data"
    },
    "POWERFLEX": {
        "LOGIN": "https://archive.powerflex.com/login",
        "ARCHIVE_01": "https://archive.powerflex.com/get_csh/0032/01",
        "ARCHIVE_02": "https://archive.powerflex.com/get_csh/0032/02"
    }
}

def get_request_base_headers():
    return {"cache-control": "no-cache", "content-type": "application/json"}


def set_authentication_headers(token):
    headers = get_request_base_headers()
    headers["Authorization"] = f"Bearer {token}"
    return headers


def get_formatted_date_components(d):
    d = datetime.datetime.today() - datetime.timedelta(days=d)
    month = f'{d.month:02}'
    day = f'{d.day:02}'
    year = f'{d.year:04}'
    return month, day, year


def get_timestamp(delta, hour_start, hour_end):
    # delta determines how many days ago
    month, day, year = date_generator(delta)
    start = int(datetime.datetime(int(year), int(month), int(day), hour_start, 0).timestamp())
    end = int(datetime.datetime(int(year), int(month), int(day), hour_end, 0).timestamp())
    return start, end


def generate_filename(prefix, data_type, date_offset, suffix):
    m, d, y = get_formatted_date_components(date_offset)
    return f"{prefix}/{data_type}/{y}-{m}-{d}.{suffix}"


def perform_login(url, username, password):
    headers = get_request_base_headers()
    login_payload = {"username": username, "password": password}
    r = requests.post(url, headers=headers, json=login_payload)
    if r.status_code == requests.codes.ok:
        return r.json()["access_token"]
    return None


def get_data(url, headers, payload):
    """
    This isn't abstracted out because it should really be a GET and not a POST,
    but the powerflex api doesn't allow it.
    """
    r = requests.post(url, headers, json=payload)
    if r.status_code == requests.codes.ok:
        return r.json()
    return None


def process_interval_data(headers, am, pm):
    """
    """
    interval_payload_am = { "measurement": "ct_response",  "time_filter": [am[0], am[1]] }
    interval_payload_pm = { "measurement": "ct_response",  "time_filter": [pm[0], pm[1]] }

    # get the AM and PM interval data
    am_data = get_data(URLS["SLAC"]["MEASUREMENT"], headers, interval_payload_am)
    pm_data = get_data(URLS["SLAC"]["MEASUREMENT"], headers, interval_payload_pm)

    # if the columns are ever different between am and pm then we have bigger problems
    columns = am_data["data"]["results"][0]["series"][0]["columns"]
    # put the data into data frames and combine them
    am_df = pd.DataFrame(data=am_data["data"]["results"][0]["series"][0]["values"], columns=columns)
    pm_df = pd.DataFrame(data=pm_data["data"]["results"][0]["series"][0]["values"], columns=columns)
    df = am_df.append(pm_df)

    # generate a csv from it
    csv_buffer = StringIO()
    pd.DataFrame(data=df).to_csv(csv_buffer, index=False)
    
    # generate a filename and save it to S3
    filename = generate_filename("raw", "interval", INTERVAL_DAY_OFFSET, "csv")
    save_csv_to_s3(csv_buffer, filename)


def process_session_data(headers, am, pm):
    pass


def save_csv_to_s3(csv_buffer, filename):
    s3_resource = boto3.resource("s3")
    s3_resource.Object(S3_BUCKET, filename).put(Body=csv_buffer.getvalue())


def _main(username, password):
    # Login to SLAC and Powerflex and get the respective tokens
    slac_token = perform_login(URLS["SLAC"]["LOGIN"], username, password)
    powerflex_token = perform_login(URLS["POWERFLEX"]["LOGIN"], username, password)

    # if either api request failed, raise an exception
    if slac_token is None:
        raise ValueError(f"Could not login to SLAC at {URLS['SLAC']['LOGIN']}")
    
    if powerflex_token is None:
        raise ValueError(f"Could not login to SLAC at {URLS['POWERFLEX']['LOGIN']}")

    # get the appropriate auth'ed headers
    slac_auth_headers = set_authentication_headers(slac_token)
    powerflex_auth_headers = set_authentication_headers(powerflex_token)

    # get the time interval we want to use for the data request, in seconds
    am_interval = get_timestamp(INTERVAL_DAY_OFFSET, AM_START, AM_END)
    pm_interval = get_timestamp(INTERVAL_DAY_OFFSET, PM_START, PM_END)
    am_session = get_timestamp(SESSION_DAY_OFFSET, AM_START, AM_END)
    pm_session = get_timestamp(SESSION_DAY_OFFSET, PM_START, PM_END)

    # lastly, request, process and save the interval and session data
    process_interval_data(slac_auth_headers, am_interval, pm_interval)
    process_session_data(powerflex_auth_headers, am_session, pm_session)





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
    response = r.json()
    print('Data Response', response)
    print('Data Response Sessions', response["sessions"])
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
    pd.DataFrame(data=df).to_csv(csv_buffer, index=False)
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
    print(headers_meas)
    df_int = pd.DataFrame()
    df_ses_1 = pd.DataFrame()
    df_ses_2 = pd.DataFrame()

    # data collected in 2 steps - works more consistently
    # larger requests to the powerflex API may fail
    hour_sets = [[0, 11], [12, 23]]

    # for hour_set in hour_sets:
    #     #print('HOUR SET', hour_set)
    #     # interval data collection - previous days data
    #     start_int, end_int = timestamp_generator(1, hour_set[0], hour_set[1])
    #     #print('INTERVAL', start_int, end_int)
    #     df_int = df_int.append(interval_data_collection(start_int, end_int, headers_meas))

    #     # session data collection - data from 10 days ago
    #     # data is updated in 7 day intervals on powerflex's side
    #     start_ses, end_ses = timestamp_generator(10, hour_set[0], hour_set[1])
    #     #print('SESSION', start_ses, end_ses)
    #     df1, df2 = session_data_collection(start_ses, end_ses, headers)

    #     df_ses_1 = df_ses_1.append(df1)
    #     df_ses_2 = df_ses_2.append(df2)

    # save_to_s3(df_int, "interval", 1)
    # save_to_s3(df_ses_1, "session", 10)
    # save_to_s3(df_ses_2, "session", 10)


if __name__ == "__main__":
    print(sys.argv)
    username = str(sys.argv[1])
    password = str(sys.argv[2])
    #main(username, password)
    _main(username, password)
