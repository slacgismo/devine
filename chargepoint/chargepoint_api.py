from zeep import Client
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta
import pandas as pd

class CP_API:
    def __init__(self):
        self.username = '92d0023b4f07baa1857381a51de78772546674ef2b8391416000751'
        self.password = 'c2f058fc77298198f5bb3089cb354053'
        self.wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
        self.client = Client(self.wsdl_url, wsse=UsernameToken(self.username, self.password))


    def getChargingSessionData(self, tStart, tEnd, stationID='null'):
        if stationID == 'null': # get all stations under API key account
            usageSearchQuery = {'fromTimeStamp': tStart, 'toTimeStamp': tEnd}
        else:
            usageSearchQuery = {'stationID': stationID, 'fromTimeStamp': tStart, 'toTimeStamp': tEnd}

        data = serialize_object(self.client.service.getChargingSessionData(usageSearchQuery)['ChargingSessionData'])
        df = pd.DataFrame(data)
        return df

    def getLoad(self, stationID):
        # This function gets the current load (kW) being consumed at the stationID
        usageSearchQuery = {'stationID': stationID}
        data = self.client.service.getLoad(usageSearchQuery)
        return data


cp = CP_API()
# SESSION
tStart = datetime(2020, 2, 13, 00, 00, 00)
tEnd = tStart + timedelta(hours=23, minutes=59, seconds=59)
session = cp.getChargingSessionData(tStart, tEnd, stationID = '1:113189')
print(session['sessionID'])

# LOAD
Load = []
stationID = ['1:113189', '1:112413', '1:113177']
for i in stationID:
    Load.append(cp.getLoad(i))
print(Load[0])