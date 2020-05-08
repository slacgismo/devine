#!/usr/bin/env python
# coding: utf-8

# In[71]:


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
#         self.username = '7f74b2f7226e5cf50d59e84cc628649f5dadd5a5234f51571673509'
#         self.password = '20287bf991b521edbd6bd2b5c83feed4'
        self.wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
        self.client = Client(self.wsdl_url, wsse=UsernameToken(self.username, self.password))

    def getSession(self, tStart, tEnd):

        usageSearchQuery = {'fromTimeStamp': tStart, 'toTimeStamp': tEnd,}
        data = self.client.service.getChargingSessionData(usageSearchQuery)
#         print('session data: ', data['ChargingSessionData'])
        df = pd.DataFrame(data['ChargingSessionData'])
        return data

    def shedLoad(self, stationID, allowedLoadStation, portNumber, allowedLoadPort, timeInterval=0):
        # load is in kW
        usageSearchQuery = {'stationID': stationID}
        pass
    
    def clearShedState(self, ):
        pass
    
    def getLoad(self):
        usageSearchQuery = {'stationID': '1:113189'}
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
data = cp.getSession(tStart, tEnd)
CPNI = cp.getLoad()


# In[72]:


CPNI


# In[54]:


# print('Data: ', data)
NewDict = {}  # Initialize a new dictionary
for listItem in data['ChargingSessionData']:
    for key, value in listItem.items():  # Loop through all dictionary elements in the list
        if key in list(NewDict):  # if the key already exists, append to new
            for entry in value:
                NewDict[key].append(entry)
        else:  # if it's a new key, simply add to the new dictionary
            NewDict[key] = value

df = pd.DataFrame(NewDict)
df.head()


# In[55]:


a = data['ChargingSessionData'][0]
a['stationID']


# In[47]:


test = serialize_object(data['ChargingSessionData'])

# data['ChargingSessionData']


# In[62]:


data['ChargingSessionData'][0]


# In[49]:


df = pd.DataFrame(test)


# In[58]:


df.head(30)


# In[57]:


data


# In[ ]:




