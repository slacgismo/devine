from zeep import Client
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta
import config
import pandas as pd
import time
import json


class CP_API:
    def __init__(self):
        self.username = config.chargepoint_api_keys['google_api_username']
        self.password = config.chargepoint_api_keys['google_api_password']
        # self.username = config.chargepoint_api_keys['slac-gismo_api_username']
        # self.password = config.chargepoint_api_keys['slac-gismo_api_password']
        # self.username = config.chargepoint_api_keys['slac_api_username']
        # self.password = config.chargepoint_api_keys['slac_api_password']
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
        return [total_load, station_data, data_load]

    def getStations(self, sgID=None):
        # Get list of stations and number of ports under an organization ID
        usageSearchQuery = {'sgID': sgID}
        data = self.client.service.getStations(usageSearchQuery)
        # print('getStations: ', data)
        # print(data) # -> uncomment this to get sgID and group name
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
        usageSearchQuery = {'Status': status, 'stationIDs': stationIDs}
        # usageSearchQuery = {'stations': stationIDs}
        data = self.client.service.getStationStatus(usageSearchQuery)
        df = serialize_object(data['stationData'])
        return df

    def getChargingSessionData(self, stationID, activeSessionsOnly=True):
        usageSearchQuery = {'activeSessionsOnly': activeSessionsOnly, 'stationID': '1:323301'}
        data = self.client.service.getChargingSessionData(usageSearchQuery)
        print(data)
        df = pd.DataFrame(serialize_object(data['ChargingSessionData']))
        print(df)
        return df

    def getStationGroups(self, orgID):
        usageSearchQuery = {'orgID': orgID}
        data = self.client.service.getStationStatus(usageSearchQuery)
        df = serialize_object(data['stationData'])
        return df

    def getGroupDetail(self, sgID='slac_B53_sgID'):
        # usageSearchQuery = {'sgID': sgID}
        usageSearchQuery = {}
        data = self.client.service.getStationGroupDetails(usageSearchQuery)
        print(data)
    # def getUpdates(self,):
    #     # get updates you are listening

start = time.time()
cp = CP_API()
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
# stations = cp.getStations(sgID=config.chargepoint_station_groups['google_B46_sgID'])
stations = cp.getStations(sgID=config.chargepoint_station_groups['google_plymouth_sgID'])
# stations = cp.getStations(sgID=config.chargepoint_station_groups['google_CRIT_sgID'])
station_list = stations['stationID'].to_list()
cp_station = {'stationID': station_list}
status = cp.getStationStatus(stationIDs=cp_station)

stations_inuse = {}
for i in status:
    num_ports = len(i['Port'])
    ports_inuse = []
    for p in i['Port']:
        if p['Status'] == 'INUSE':
            ports_inuse.append(p['portNumber'])
    if len(ports_inuse) > 0:
        stations_inuse[i['stationID']] = ports_inuse

# dictionary with stations ports and status
stations_status = {}
for i in status:
    number_port = '-1'
    status_port = 'INITIALIZING'
    port_status = []
    for p in i['Port']:
        status_port = p['Status']
        number_port = p['portNumber']
        port_status.append((number_port, status_port))
    stations_status[i['stationID']] = port_status


retval = []
# for i in stations_inuse:
#     ret = cp.getStationLoad(queryID=i)[-1]
#     station_data = ret['stationData'][0]
#     # print(station_data)
#     load = []
#     for p in range(len(stations_inuse[i])):
#         port_num = int(stations_inuse[i][p])
#         load.append(station_data['Port'][port_num-1])
#     retval.append({'stationID':i, 'Port':load})
# print(retval)

# for i in stations_status:
#     ret = cp.getStationLoad(queryID=i)[-1]
#     station_data = ret['stationData'][0]
#     # print(station_data)
#     load = []
#     for p in range(len(stations_status[i])):
#         port_num = int(stations_status[i][p])
#         load.append(station_data['Port'][port_num-1])
#     retval.append({'stationID':i, 'Port':load})
# print(retval)

# print('Time: ', time.time()-start)

# Printing response code
# for i in station_list:
#     resp_code = cp.getStationLoad(queryID=i)[-1]['responseCode']
#     if resp_code != '100':
#         print('Station: ', i)
#         print('Response Code: ', resp_code)
# print('Done!')
#
# def parser_cp(data):
#     stations = []
#     ports = []
#     loads = []
#     for d in data:
#         stations.append(d['stationID'])
#         for p in d['Port']:
#             ports.append(p['portNumber'])
#             loads.append(float(p['portLoad']))
#     return stations, ports, loads
#
#
# parser_cp(retval)




# {'stationID': 'ID', 'Port': [{'Port':'X', 'Power(kW)':'Y'}]}





