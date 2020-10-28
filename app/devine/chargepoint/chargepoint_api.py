from zeep import Client
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta
from . import config
import pandas as pd
import json


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

        total_load = data_load['sgLoad']
        station_data = serialize_object(data_load['stationData'])
        station_load = data_load['stationData'][0]['stationLoad']

        return [total_load, station_data,station_load, data_load]#TODO

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
        usageSearchQuery = {'Status': status, 'stations': stationIDs, 'portDetails':True}
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

def parsePort(data, port_status,port_power):
    res={
        'port_number':data['portNumber'],
        'port_status':port_status,
        'shed_state':data['shedState'],
        'port_load':data['portLoad'],
        'allowed_load':data['allowedLoad'],
        'port_power':port_power,
        'user_id':data['userID']
    }
    return res

def getData(name):
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
    status = cp.getStationStatus(stationIDs=station_list)
    
    print(len(status))
    stations_inuse = {}
    for i in status:
        num_ports = len(i['Port'])
        ports_each = []
        for p in i['Port']:
            # print('-'*100)
            # print(p['Status'])
            # if p['Status'] != 'INUSE':
            ports_each.append([p['portNumber'],p['Status'], p['Power']])
        if len(ports_each) > 0:
            stations_inuse[i['stationID']] = ports_each
    ii=0
    retval = []
    for i in stations_inuse:
        _,_,station_load,ret = cp.getStationLoad(queryID=i)
        station_data = ret['stationData'][0]
        load = []

        for p in range(len(stations_inuse[i])): #how many ports
            port_num = int(stations_inuse[i][p][0]) #the port#
            port_status = stations_inuse[i][p][1]
            port_power = stations_inuse[i][p][2]
            load.append(parsePort(station_data['Port'][port_num-1], port_status, port_power))
            # parsePort(station_data['Port'][port_num-1], port_status)
        retval.append({'station_id':i, 'station_load':station_load, 'Port':load})
        ii+=1
        print(name[1]+str(ii))
    # print(retval)
    return retval

def read_from_sites():
    sites=[['slac-gismo', 'slac_GISMO_sgID'],
           ['slac', 'slac_B53_sgID'],
           ['google', 'google_plymouth_sgID'],
           ['google', 'google_B46_sgID'],
           ['google', 'google_CRIT_sgID']]
    retval = []
    for site in sites:
        retval.append(getData(site))
        print('finish #')
    return retval


# def parser_cp(data):
#     stations = []
#     ports = []
#     loads = []
#     for d in data:
#         stations.append(d['station_id'])
#         for p in d['Port']:
#             ports.append(p['port_number'])
#             loads.append(float(p['port_load']))
#     return stations, ports, loads


# parser_cp(retval)




# {'stationID': 'ID', 'Port': [{'Port':'X', 'Power(kW)':'Y'}]}





