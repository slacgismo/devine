from zeep import Client
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta
from . import config
import pandas as pd
import json
import time

class CP_API:
    def __init__(self, site):
        # self.username = config.chargepoint_api_keys['google_api_username']
        # self.password = config.chargepoint_api_keys['google_api_password']
        # self.username = config.chargepoint_api_keys['slac-gismo_api_username']
        # self.password = config.chargepoint_api_keys['slac-gismo_api_password']
        self.username = config.chargepoint_api_keys['{}_api_username'.format(site)]
        self.password = config.chargepoint_api_keys['{}_api_password'.format(site)]
        self.wsdl_url = "https://webservices.chargepoint.com/cp_api_5.1.wsdl"
        self.client = Client(self.wsdl_url, wsse=UsernameToken(self.username, self.password))

    def getSession(self, tStart, tEnd):
        # This call retrieves final session summaries for a station owner’s (organization’s) charging station(s)based
        # on search criteria
        usageSearchQuery = {'fromTimeStamp': tStart, 'toTimeStamp': tEnd, }
        data_session = self.client.service.getChargingSessionData(usageSearchQuery)
        df = pd.DataFrame(serialize_object(data_session['ChargingSessionData']))
        return df

    def getIntervalData(self, sessionID):
        # This call retrieves final session summaries for a station owner’s (organization’s) charging station(s)based
        # on search criteria
        usageSearchQuery = {'sessionID': sessionID}
        data_session = self.client.service.get15minChargingSessionData(
            usageSearchQuery)  # Getting encoding violation error
        # df = pd.DataFrame(serialize_object(data_session['ChargingSessionData']))
        return data_session

    def getStationLoad(self,queryID='1:5447121'):
        # Use this call to retrieve the load and shed state for a single station or custom
        # station group.This method also returns the load for each port on a multi-port station.
        usageSearchQuery = {'stationID': queryID}
        data_load = self.client.service.getLoad(usageSearchQuery)
        # total_load = data_load['sgLoad']
        # station_data = serialize_object(data_load['stationData'])
        station_load = data_load['stationData'][0]['stationLoad']
        return [station_load, data_load]

    def getStations(self, organizationName='SLAC - Stanford', sgID=None):
        # Get list of stations and number of ports under an organization ID
        usageSearchQuery = {'organizationName': organizationName, 'sgID': sgID}
        data = self.client.service.getStations(usageSearchQuery)
        # print(data) -> uncomment this to get sgID and group name
        df = pd.DataFrame(serialize_object(data['stationData']))
        return df[['stationID', 'numPorts']]

    def getUsers(self):
        # Get list of stations and number of ports under an organization ID
        usageSearchQuery = {}
        data = self.client.service.getUsers(usageSearchQuery)
        df = pd.DataFrame(serialize_object(data['users']['user']))
        return df['userID']

    def getStationStatus(self, status=None, stationIDs=None):
        # Get list of available stations
        usageSearchQuery = {'Status': status, 'stationIDs': stationIDs, 'portDetails':True}
        # usageSearchQuery = {'stations': stationIDs}
        data = self.client.service.getStationStatus(usageSearchQuery)
        df = serialize_object(data['stationData'])
        return df

    def getStationGroups(self, orgID):
        usageSearchQuery = {'orgID': orgID}
        data = self.client.service.getStationStatus(usageSearchQuery)
        df = serialize_object(data['stationData'])
        return df
    # def getUpdates(self,):
    #     # get updates you are listening

def parsePort(data, port_num, port_status,port_power, port_timestamp):
    res={
        'port_number':port_num,
        'port_status':port_status,
        'shed_state':data['shedState'],
        'port_load':data['portLoad'],
        'allowed_load':data['allowedLoad'],
        'port_power':port_power,
        'user_id':data['userID'],
        'port_timestamp':port_timestamp
    }
    return res

def getData(name):
    start = time.time()
    site = name[0]
    api_group = name[1]
    cp = CP_API(site)
    tStart = datetime(2020, 2, 13, 00, 00, 00)
    tEnd = tStart + timedelta(hours=23, minutes=59, seconds=59)
    # session = cp.getSession(tStart, tEnd)
    # load = cp.getStationLoad()
    # stations = cp.getStations(organizationName='SLAC Research Group')
    # stationStatus = cp.getStationStatus(status=1)
    # sessionList = session['sessionID']
    # interval = cp.getIntervalData(sessionList[0])
    # users = cp.getUsers()
    # stations = cp.getStations(sgID=config.chargepoint_station_groups['slac_B53_sgID'])
    stations = cp.getStations(sgID=config.chargepoint_station_groups[api_group])
    station_list = stations['stationID'].to_list()
    cp_station = {'stationID': station_list}
    status = cp.getStationStatus(stationIDs=cp_station)
    # print(len(station_list))
    # print('Time1: ', time.time()-start)
    stations_inuse = {}
    stations_notuse = {}
    for i in status:
        num_ports = len(i['Port'])
        ports_inuse = []
        ports_notuse = []
        for p in i['Port']:
            # print('-'*100)
            # print(p['Status'])
            if p['Status'] == 'INUSE':
                ports_inuse.append([p['portNumber'],p['Status'], p['Power'], p['TimeStamp']])
            else:
                ports_notuse.append([p['portNumber'],p['Status'], p['Power'], p['TimeStamp']])
        if len(ports_inuse) > 0:
            stations_inuse[i['stationID']] = ports_inuse
        if len(ports_notuse) > 0:
            stations_notuse[i['stationID']] = ports_notuse
    ii=0
    retval = []
    station_load_map = {} #save the station_load to avoid getLoad again when ports not use
    for i in stations_inuse:
        station_load,ret = cp.getStationLoad(queryID=i)
        station_data = ret['stationData'][0]
        station_load_map[i] = station_load
        load = []
        for p in range(len(stations_inuse[i])): #how many ports
            port_num = int(stations_inuse[i][p][0]) #the port#
            port_status = stations_inuse[i][p][1]
            port_power = stations_inuse[i][p][2]
            port_timestamp = stations_inuse[i][p][3]
            load.append(parsePort(station_data['Port'][port_num-1], port_num, port_status, port_power, port_timestamp))
            # parsePort(station_data['Port'][port_num-1], port_status)
        retval.append({'station_id':i, 'station_load':station_load, 'Port':load})
        ii+=1
        print(name[1]+str(ii))

    for j in stations_notuse:
        station_load_notuse = 0.000
        if j in station_load_map:
            station_load_notuse = station_load_map[j]
        load_notuse = []
        for q in range(len(stations_notuse[j])):
            port_num_notuse = int(stations_notuse[j][q][0]) #the port#
            port_status_notuse = stations_notuse[j][q][1]
            port_power_notuse = stations_notuse[j][q][2]
            port_timestamp_notuse = stations_notuse[j][q][3]
            data_notuse={
                'shedState': 0,
                'portLoad':0.000,
                'allowedLoad':0.000,
                'userID': '',
            }
            load_notuse.append(parsePort(data_notuse, port_num_notuse, port_status_notuse, port_power_notuse, port_timestamp_notuse))
        retval.append({'station_id':j, 'station_load':station_load_notuse, 'Port':load_notuse})
        
    # print(retval)
    return retval

def read_from_sites():
    start = time.time()
    sites=[['slac-gismo', 'slac_GISMO_sgID'],
           ['slac', 'slac_B53_sgID'],
           ['google', 'google_CRIT_sgID'],
           ['google', 'google_B46_sgID'],
           ['google', 'google_plymouth_sgID']]
    retval = []
    for site in sites:
        retval.append(getData(site))
        print('finish #')
    # print(retval)
    print('Total Time: ', time.time()-start)
    return retval


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