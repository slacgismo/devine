import config
import requests
import json



class Viriciti():
    def __init__ (self):
        self.key = config.key
        self.urlAssets = config.endpointAssets
        self.urlHist = config.endpointHist
        self.headers =  config.headers

    def getAssets(self, time, busID, label):
        # headers = {'x-api-key':config.key}
        try:
            response = requests.request("GET", self.urlAssets, headers=self.headers)
            return json.loads(response.text)
        except Exception as e:
            print('request error: ', e)
            return response.status_code

    def historical(self, busID, label, time):
        endpoint =self.urlHist+busID+'?label='+label+'&start='+str(time[0]*1000)+'&end='+str(time[1]*1000)+'&step=60000'
        try:
            payload={}
            response = requests.request("GET", endpoint, headers=self.headers,data=payload)
            return json.loads(response.text)
        except Exception as e:
            print('request error: ', e)
            return response.status_code


if __name__ == '__main__':
    busMapping = json.load(open('map_vid.json'))
    bus = Viriciti()
    label_dict = {'soc':'soc','odometer':'odo', 'amps':'current', 'volts':'voltage', 'power':'power', 'km/day':'distance_driven_per_day', 'kwh/day':'energy_used_per_day', 'gps':'gps'}
    label = 'soc'
    busID = 'sf_022'
    time = (1632246031, 1632264397)
    bus_data = bus.historical(busID=busID, label=label,time=time)


