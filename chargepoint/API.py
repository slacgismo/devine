#!/usr/bin/env python
# coding: utf-8

# In[28]:


from zeep import Client
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken
from zeep import xsd
from datetime import datetime, timedelta
import pandas as pd
import json

class CP_API:
    def __init__(self):
        self.username = '92d0023b4f07baa1857381a51de78772546674ef2b8391416000751'
        self.password = 'c2f058fc77298198f5bb3089cb354053'
#         self.username = '7f74b2f7226e5cf50d59e84cc628649f5dadd5a5234f51571673509'
#         self.password = '20287bf991b521edbd6bd2b5c83feed4'
        self.wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
        self.client = Client(self.wsdl_url, wsse=UsernameToken(self.username, self.password))

#     def getSession(self, tStart, tEnd):

#         usageSearchQuery = {'fromTimeStamp': tStart, 'toTimeStamp': tEnd,}
#         data = serialize_object(self.client.service.getChargingSessionData(usageSearchQuery)['ChargingSessionData'])
#         df = pd.DataFrame(data)
#         return df

    def getChargingSessionData(self, tStart, tEnd):

        usageSearchQuery = {'fromTimeStamp': tStart, 'toTimeStamp': tEnd,}
        data = serialize_object(self.client.service.getChargingSessionData(usageSearchQuery)['ChargingSessionData'])
        df = pd.DataFrame(data)
        return df
    
    def get15minChargingSessionData(self, sessionID, energyConsumedInterval=False):
        value = xsd.AnyObject(xsd.Long, sessionID)
        usageSearchQuery = {'sessionID': value, 'energyConsumedInterval': energyConsumedInterval}
        data = self.client.service.get15minChargingSessionData(usageSearchQuery)
        return data
    
    def shedLoad(self, stationID, allowedLoadStation, portNumber, allowedLoadPort, timeInterval=0):
        # load is in kW
        usageSearchQuery = {'stationID': stationID}
        pass
    
    def clearShedState(self, ):
        pass
    
    def getLoad(self, stationID):
        usageSearchQuery = {'stationID': stationID}
        data = self.client.service.getLoad(usageSearchQuery)
        return data
    
    def getCPNInstance(self):
        data = self.client.service.getCPNInstances()
        return data
    
    def getOrgsAndStationsGroups(self):
        data = self.client.service.getCPNInstances()
        return data
    
    
    
cp = CP_API()
tStart = datetime(2020, 2, 13, 00, 00, 00)
tEnd = tStart + timedelta(hours=23, minutes=59, seconds=59)
data = cp.getChargingSessionData(tStart, tEnd)
# data15 = cp.get15minChargingSessionData(sessionID='658538251') # Throwing error -> need to fix/ask CP
# CPNI = cp.getLoad()
# 1:112413, 1:113177, 


# In[14]:


data


# In[6]:


CPNI = []
stationID = ['1:113189', '1:112413', '1:113177']
for i in stationID:
    CPNI.append(cp.getLoad(i))
CPNI


# In[57]:


data


# In[3]:


get_ipython().system('jupyter nbconvert --to script API.ipynb')


# In[ ]:




