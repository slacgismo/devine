from zeep import Client
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta
import pandas as pd

# username = '92d0023b4f07baa1857381a51de78772546674ef2b8391416000751'
# password = 'c2f058fc77298198f5bb3089cb354053'
#
# wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
# client = Client(wsdl_url, wsse=UsernameToken(username, password))
#
# tStart=datetime(2020, 2, 13, 00, 00, 00)
# tEnd = tStart + timedelta(hours=23, minutes=59, seconds=59)
# usageSearchQuery = {
#     'fromTimeStamp': tStart,
#     'toTimeStamp': tEnd,
# }
# data = client.service.getChargingSessionData(usageSearchQuery)
# print("Number of records in time-frame: ", len(data.ChargingSessionData))
# print('data response: ', data)
#
# ## Fill Sessions Table
# for d in data.ChargingSessionData:
#     ## enclose in try-except to avoid TypeError: int() argument must be a string or a number, not 'NoneType'
#     ## when userID is None, and other errors
#     try:
#         row_session = [int(d.sessionID), d.startTime.strftime('%Y-%m-%d %H:%M:%S'),
#                         d.endTime.strftime('%Y-%m-%d %H:%M:%S'), float(d.Energy),
#                         str(d.stationID), int(d.userID), str(d.credentialID), int(d.portNumber)]
#         # print('Row Session: ', row_session)
#     except:
#         pass

class CP_API:
    def __init__(self):
        self.username = '92d0023b4f07baa1857381a51de78772546674ef2b8391416000751'
        self.password = 'c2f058fc77298198f5bb3089cb354053'
        self.wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
        self.client = Client(self.wsdl_url, wsse=UsernameToken(self.username, self.password))

    def getSession(self, tStart, tEnd):

        usageSearchQuery = {'fromTimeStamp': tStart, 'toTimeStamp': tEnd,}
        data = self.client.service.getChargingSessionData(usageSearchQuery)
        print('session data: ', data['ChargingSessionData'])
        df = pd.DataFrame(data['ChargingSessionData'])
        print(df.head())

cp = CP_API()
tStart = datetime(2020, 2, 13, 00, 00, 00)
tEnd = tStart + timedelta(hours=23, minutes=59, seconds=59)
cp.getSession(tStart, tEnd)