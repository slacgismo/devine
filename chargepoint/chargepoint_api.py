from zeep import Client
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta
import pandas as pd
import json


class CP_API:
    def __init__(self):
        self.username = '92d0023b4f07baa1857381a51de78772546674ef2b8391416000751'
        self.password = 'c2f058fc77298198f5bb3089cb354053'
        self.wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
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

    def getStationLoad(self):
        # Use this call to retrieve the load and shed state for a single station or custom
        # station group.This method also returns the load for each port on a multi-port station.
        usageSearchQuery = {'stationID': '1:113189'}
        data_load = self.client.service.getLoad(usageSearchQuery)
        total_load = data_load['sgLoad']
        station_data = serialize_object(data_load['stationData'])
        return [total_load, station_data, data_load]

    def getStations(self, organizationName='SLAC - Stanford'):
        # Get list of stations and number of ports under an organization ID
        usageSearchQuery = {'organizationName': organizationName}
        data = self.client.service.getStations(usageSearchQuery)
        df = pd.DataFrame(serialize_object(data['stationData']))
        return df[['stationID', 'numPorts']]

    def getUsers(self):
        # Get list of stations and number of ports under an organization ID
        usageSearchQuery = {}
        data = self.client.service.getUsers(usageSearchQuery)
        df = pd.DataFrame(serialize_object(data['users']['user']))
        return df['userID']

    def getStationStatus(self, status=1):
        # Get list of available stations
        usageSearchQuery = {'Status': status}
        data = self.client.service.getStationStatus(usageSearchQuery)
        df = serialize_object(data['stationData'])
        return df

    # def getUpdates(self,):
    #     # get updates you are listening


cp = CP_API()
tStart = datetime(2020, 2, 13, 00, 00, 00)
tEnd = tStart + timedelta(hours=23, minutes=59, seconds=59)
# session = cp.getSession(tStart, tEnd)
load = cp.getStationLoad()
# stations = cp.getStations()
# stationStatus = cp.getStationStatus(status=1)
# sessionList = session['sessionID']
# interval = cp.getIntervalData(sessionList[0])
# users = cp.getUsers()

