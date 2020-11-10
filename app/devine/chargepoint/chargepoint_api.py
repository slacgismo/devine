from zeep import Client
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta
from . import config
import pandas as pd
import json
import time
from django.utils import timezone
import pytz


class chargePointApi:
    def __init__(self, site):
        self.site = site
        self.timestamp = timezone.now()
        self.username = config.chargepoint_api_keys['{}_api_username'.format(site)]
        self.password = config.chargepoint_api_keys['{}_api_password'.format(site)]
        self.wsdl_url = "https://webservices.chargepoint.com/cp_api_5.1.wsdl"
        self.client = Client(self.wsdl_url, wsse=UsernameToken(self.username, self.password))

    def get_station_load(self, query_id='1:5447121'):
        # Use this call to retrieve the load and shed state for a single station or custom
        # station group.This method also returns the load for each port on a multi-port station.
        usage_search_query = {'stationID': query_id}
        data_load = self.client.service.getLoad(usage_search_query)
        station_load = data_load['stationData'][0]['stationLoad']
        return station_load, data_load, data_load['responseCode'], data_load['responseText']

    def get_stations(self, organization_name='SLAC - Stanford', sg_id=None):
        # Get list of stations and number of ports under an organization ID
        usage_search_query = {'organizationName': organization_name, 'sgID': sg_id}
        data = self.client.service.getStations(usage_search_query)
        df = pd.DataFrame(serialize_object(data['stationData']))
        return df[['stationID', 'numPorts']], data['responseCode'], data['responseText']

    def get_station_status(self, status=None, station_ids=None):
        # Get list of available stations
        usage_search_query = {'Status': status, 'stationIDs': station_ids, 'portDetails': True}
        data = self.client.service.getStationStatus(usage_search_query)
        df = serialize_object(data['stationData'])
        return df, data['responseCode'], data['responseText']

    def get_charging_session_data(self,
                               station_id=None,
                               activeSessionsOnly=False,
                               time_start=None,
                               time_end=None):
        usage_search_query = {
            'stationID': station_id,
            'activeSessionsOnly': activeSessionsOnly,
            'fromTimeStamp': time_start,
            'toTimeStamp': time_end
        }
        data = self.client.service.getChargingSessionData(usage_search_query)
        df = serialize_object(data['ChargingSessionData'])
        return df, data['responseCode'], data['responseText']

    # Devine-> 5min/ opti session table: session ID, group name, session start, timestamp, user ID, energy
    # parameter: station_ids, the stations in this group, can obtain from getStationsbyGroup()
    def get_charging_active_session_data(self, group, station_ids=None):
        res = [True]
        for station_id in station_ids:
            sessions, resp_code, resp_text = self.get_charging_session_data(station_id, True)
            if resp_code != '100' and resp_code != '136':
                return [False, resp_code, resp_text]
            if not sessions:
                continue
            for element in sessions:
                session = {}
                session['sessionID'] = element['sessionID']
                session['groupName'] = group
                session['startTime'] = element['startTime']
                session['userID'] = element['userID']
                session['energy'] = element['Energy']
                session['timestamp'] = self.timestamp
                res.append(session)
        return res

    #Devine-> 1day/ UI session table: session ID, group name, session start, end, timestamp, user ID, energy
    # parameter: station_ids, the stations in this group, can obtain from getStationsbyGroup()
    def get_charging_daily_session_data(self, group, station_ids=None, time_start=None, time_end=None):
        res = []
        for station_id in station_ids:
            sessions, resp_code, resp_text = self.get_charging_session_data(
                station_id, False, time_start, time_end)
            if resp_code != '100' and resp_code != '136':
                return [False, resp_code, resp_text]
            if not sessions:
                continue
            for element in sessions:
                session = {}
                session['sessionID'] = element['sessionID']
                session['groupName'] = group
                session['startTime'] = element['startTime']
                session['endTime'] = element['endTime']
                session['userID'] = element['userID']
                session['energy'] = element['Energy']
                session['timestamp'] = self.timestamp
                res.append(session)
        return res


def parse_port_data(data, port_num, port_status, port_power, port_timestamp):
    res = {
        'port_number': port_num,
        'port_status': port_status,
        'shed_state': data['shedState'],
        'port_load': data['portLoad'],
        'allowed_load': data['allowedLoad'],
        'port_power': port_power,
        'user_id': data['userID'],
        'port_timestamp': port_timestamp,
        'session_id': data['sessionID'],
    }
    return res


def get_data(name, ret_session):
    start = time.time()
    site = name[0]
    api_group = name[1]
    cp = chargePointApi(site)

    stations, resp_code, resp_text = cp.get_stations(
        sg_id=config.chargepoint_station_groups[api_group])
    if resp_code != '100':
        return [False, resp_code, resp_text]
    station_list = stations['stationID'].to_list()

    # Get Station Status
    cp_station = {'stationID': station_list}
    status, resp_code, resp_text = cp.get_station_status(station_ids=cp_station)
    if resp_code != '100':
        return [False, resp_code, resp_text]

    stations_inuse = {}
    stations_notuse = {}
    inuse_station_list = []
    for i in status:
        num_ports = len(i['Port'])
        ports_inuse = []
        ports_notuse = []
        for p in i['Port']:
            if p['Status'] == 'INUSE':
                ports_inuse.append([p['portNumber'], p['Status'], p['Power'], p['TimeStamp']])
            else:
                ports_notuse.append([p['portNumber'], p['Status'], p['Power'], p['TimeStamp']])
        if len(ports_inuse) > 0:
            stations_inuse[i['stationID']] = ports_inuse
            inuse_station_list.append(i['stationID'])
        if len(ports_notuse) > 0:
            stations_notuse[i['stationID']] = ports_notuse

    # Get session EVERY 5min
    print('-' * 100)
    print(inuse_station_list)
    active_session_list = cp.get_charging_active_session_data(name[2], inuse_station_list)
    if active_session_list[0] == False:
        return active_session_list
    active_session_list.pop(0)
    for session in active_session_list:
        ret_session.append(session)
    print('\n Active Session Finished Loading \n')

    # Get INUSE Load
    ret_value = [True]
    station_load_map = {}  #save the station_load to avoid getLoad again when ports not use
    for i in stations_inuse:
        station_load, ret, resp_code, resp_text = cp.get_station_load(query_id=i)
        if resp_code != '100':
            return [False, resp_code, resp_text]
        station_data = ret['stationData'][0]
        station_load_map[i] = station_load
        load = []
        for p in range(len(stations_inuse[i])):  #how many ports
            port_num = int(stations_inuse[i][p][0])  #the port#
            port_status = stations_inuse[i][p][1]
            port_power = stations_inuse[i][p][2]
            port_timestamp = stations_inuse[i][p][3]
            load.append(
                parse_port_data(station_data['Port'][port_num - 1], port_num, port_status,
                          port_power, port_timestamp))
            # parse_port_data(station_data['Port'][port_num-1], port_status)
        ret_value.append({
            'station_id': i,
            'group_name': name[2],
            'station_load': station_load,
            'Port': load
        })

    # Get NOTUSE Load
    for j in stations_notuse:
        station_load_notuse = 0.000
        if j in station_load_map:
            station_load_notuse = station_load_map[j]
        load_notuse = []
        for q in range(len(stations_notuse[j])):
            port_num_notuse = int(stations_notuse[j][q][0])  #the port#
            port_status_notuse = stations_notuse[j][q][1]
            port_power_notuse = stations_notuse[j][q][2]
            port_timestamp_notuse = stations_notuse[j][q][3]
            data_notuse = {
                'shedState': 0,
                'portLoad': 0.000,
                'allowedLoad': 0.000,
                'userID': '',
                'sessionID': '',
            }
            load_notuse.append(
                parse_port_data(data_notuse, port_num_notuse, port_status_notuse, port_power_notuse,
                          port_timestamp_notuse))
        ret_value.append({
            'station_id': j,
            'group_name': name[2],
            'station_load': station_load_notuse,
            'Port': load_notuse
        })

    return ret_value


def read_all_groups():
    start = time.time()
    sites = [['slac-gismo', 'slac_GISMO_sgID', 'slac_GISMO'],
             ['slac', 'slac_B53_sgID', 'slac_B53'],
             ['google', 'google_CRIT_sgID', 'google_CRIT'],
             ['google', 'google_B46_sgID', 'google_B46'],
             ['google', 'google_plymouth_sgID', 'google_plymouth']]
    ret_general = []
    ret_session = []
    for site in sites:
        ret = get_data(site, ret_session)
        if ret[0] == False:
            return ret
        ret.pop(0)
        ret_general.append(ret)
        print('finish #' + site[2])

    print('Total Chargepoint Time: ', time.time() - start)
    return True, ret_general, ret_session


def read_daily_sessions(time_start):  # Should be Given a time_start
    start = time.time()
    sites = [['slac-gismo', 'slac_GISMO_sgID', 'slac_GISMO'],
             ['slac', 'slac_B53_sgID', 'slac_B53'],
             ['google', 'google_CRIT_sgID', 'google_CRIT'],
             ['google', 'google_B46_sgID', 'google_B46'],
             ['google', 'google_plymouth_sgID', 'google_plymouth']]
    daily_sessions = []
    ret_value = []
    for site in sites:
        start = time.time()
        cp = chargePointApi(site[0])
        time_end = time_start + timedelta(hours=23, minutes=59, seconds=59)

        stations, resp_code, resp_text = cp.get_stations(
            sg_id=config.chargepoint_station_groups[site[1]])
        station_list = stations['stationID'].to_list()

        # Get session EVERY DAY
        daily_sessions = cp.get_charging_daily_session_data(site[2], station_list, time_start, time_end)
        for session in daily_sessions:
            ret_value.append(session)

    print('Total DailySessions Time: ', time.time() - start)
    return ret_value


#########################################################################################
#                           Hidden Problem:                                             #
# Testing ALL the station-ports from five groups, by only this file                     #
#                       station-ports amounts                                           #
# slac_GISMO_sgID:      1                                                               #
# slac_B53_sgID:        3                                                               #
# google_CRIT_sgID:     29                                                              #
# google_B46_sgID:      48                                                              #
# google_plymouth_sgID: 32                                                              #
#                                                                                       #
# Takes Time: 267.559 seconds                                                           #
# (nearly 5 minutes)                                                                    #
#                                                                                       #
# 10/28/2020 Zixiong                                                                    #
#########################################################################################