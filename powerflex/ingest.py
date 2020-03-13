import sys
import s3fs
import json
import time
import boto3
import requests
import datetime
import pandas as pd
from io import StringIO
from botocore.exceptions import ClientError

# specify the offset, in days, for the request of interval and session data
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
    """
    Every single request REQUIRES these headers at a minimum
    Here we provide a simple, testable way to ensure the base headers
    are what they should be
    """
    return {"cache-control": "no-cache", "content-type": "application/json"}


def set_authentication_headers(token):
    """
    Provides a mechanism for the caller to update the base headers with the 
    authentication params for a given request. In this particular case, we
    expect a token, which we then set on the base headers as:
    Authorization: Bearer {token}
    """
    headers = get_request_base_headers()
    headers["Authorization"] = f"Bearer {token}"
    return headers


def get_date_obj_from_offset(d):
    """
    Return a date obj calculated from the given offset off of today
    """
    return datetime.datetime.today() - datetime.timedelta(days=d)


def get_formatted_date_components(d):
    """
    Given a day count offset (as Int), calculate the datetime delta as
    today - given_day_offset. The result we use to tokenize, as strings,
    the Month, Day and Year. That gets returned to the client in a tuple
    """
    month = f'{d.month:02}'
    day = f'{d.day:02}'
    year = f'{d.year:04}'
    return month, day, year


def get_timestamp(d, hour_start, hour_end):
    """
    Given a day offset, retrieve a start and end timestamp (in seconds, since 01.01.1970)
    Return the start and end times as a tuple
    """
    # delta determines how many days ago
    month, day, year = get_formatted_date_components(d)
    utc_start = datetime.datetime(int(year), int(month), int(day), hour_start, 0).replace(tzinfo=datetime.timezone.utc)
    utc_end = datetime.datetime(int(year), int(month), int(day), hour_end, 0).replace(tzinfo=datetime.timezone.utc)
    start = int(utc_start.timestamp())
    end = int(utc_end.timestamp())
    return start, end


def generate_filename_and_path(prefix, data_type, dt, suffix, discrete_token=""):
    """
    Return a standard naming convention and S3 path to save files to.
    """
    m, d, y = get_formatted_date_components(dt)
    return f"{prefix}/{data_type}/{y}-{m}-{d}{discrete_token}.{suffix}"


def perform_login(url, username, password):
    """
    Authenticate a user and retrieve the associated bearer token
    """
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
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == requests.codes.ok:
        return r.json()

    print(f"Could not retrieve data from {url}. Status Code: {r.status_code}")
    return None


def process_interval_data(headers, intervals):
    """
    Attempt to retrieve interval data for the given interval. If successfully
    retrieved, save it to s3, otherwise, raise a ValueError
    """
    df = pd.DataFrame()
    for entry in intervals:
        interval_payload = {"measurement": "ct_response",  "time_filter": [entry[0], entry[1]]}
        data = get_data(URLS["SLAC"]["MEASUREMENT"], headers, interval_payload)
        
        if data is None:
            raise ValueError(f"Could not retrieve interval data; request failed")

        columns = data["data"]["results"][0]["series"][0]["columns"]    
        df = df.append(pd.DataFrame(data=data["data"]["results"][0]["series"][0]["values"], columns=columns))

    # generate a csv from it
    csv_buffer = StringIO()
    pd.DataFrame(data=df).to_csv(csv_buffer, index=False)
    
    # generate a filename and save it to S3
    dt = get_date_obj_from_offset(INTERVAL_DAY_OFFSET)
    filename = generate_filename_and_path("raw", "interval", dt, "csv")
    save_csv_to_s3(csv_buffer, filename)


def process_session_data(headers, intervals):
    """
    Attempt to retrieve session data for the given interval. If successfully
    retrieved, save it to s3, otherwise, raise a ValueError
    """
    df_session_1 = pd.DataFrame()
    df_session_2 = pd.DataFrame()
    for entry in intervals:
        # establish the payload to send to the powerflex api
        session_payload = {"startTime": entry[0], "stopTime": entry[1], "filterBy": "sessionStopTime", "anonymize": True}
        
        # request the data
        session_data_1 = get_data(URLS["POWERFLEX"]["ARCHIVE_01"], headers, session_payload)
        session_data_2 = get_data(URLS["POWERFLEX"]["ARCHIVE_02"], headers, session_payload)

        if session_data_1 is None or session_data_2 is None:
            raise ValueError(f"Could not retrieve session data; request failed")
        
        # put it into a data frame so we can more easily convert it to a csv
        df_session_1 = df_session_1.append(pd.DataFrame(session_data_1["sessions"]))
        df_session_2 = df_session_2.append(pd.DataFrame(session_data_2["sessions"]))

    # iterate over the data frames, convert it to a csv and save it to s3
    for index, df in enumerate([df_session_1, df_session_2]):
        # generate a csv from pandas DF
        csv_buffer = StringIO()
        pd.DataFrame(data=df).to_csv(csv_buffer, index=False)
        
        # generate a filename and save it to S3
        dt = get_date_obj_from_offset(SESSION_DAY_OFFSET)
        filename = generate_filename_and_path("raw", f"session", dt, "csv", f"-{str(index)}")
        save_csv_to_s3(csv_buffer, filename)


def save_csv_to_s3(csv_buffer, filename):
    """
    Write a given csv buffer to S3
    """
    try:
        s3_resource = boto3.resource("s3")
        s3_resource.Object(S3_BUCKET, filename).put(Body=csv_buffer.getvalue())
    except ClientError as e:
        print(f"Unexpected client error while communicating with S3 via boto: {e}")


def main(username, password):
    try:
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
        interval_datetime = get_date_obj_from_offset(INTERVAL_DAY_OFFSET)
        session_datetime = get_date_obj_from_offset(SESSION_DAY_OFFSET)
        
        am_interval = get_timestamp(interval_datetime, AM_START, AM_END)
        pm_interval = get_timestamp(interval_datetime, PM_START, PM_END)
        am_session = get_timestamp(session_datetime, AM_START, AM_END)
        pm_session = get_timestamp(session_datetime, PM_START, PM_END)

        # lastly, request, process and save the interval and session data
        try:
            process_interval_data(slac_auth_headers, [am_interval, pm_interval])
            process_session_data(powerflex_auth_headers, [am_session, pm_session])
        except ValueError as e:
            print(e)
    
    except requests.exceptions.ConnectionError as e:
        print("Looks like we can't access the internet right now...😑")


if __name__ == "__main__":
    username = str(sys.argv[1])
    password = str(sys.argv[2])
    main(username, password)
