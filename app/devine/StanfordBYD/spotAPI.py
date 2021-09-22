
import config
import requests
import pandas as pd
import pickle
from datetime import datetime
import time as t

# Configuration
baseURL = config.baseURL
endURL = config.endURL
get_vehicles = 'get_vehicles'

# Loading Route vs Map
route_mapping = pd.read_pickle('routeMapping.pickle')

def compareList(l1,l2):
    l1.sort()
    l2.sort()
    print(l1)
    print(l2)
    if (l1 == l2):
        print('lists are equal')
        return True
    else:
        print('lists are NOT equal')
        return False

def getBusRoute():
    try:
        resp = requests.get(url=baseURL + get_vehicles + endURL)
    except Exception as e:
        print(e)
        return None
    retval_vehicles = resp.json()[get_vehicles]
    listRoute = []
    listBus = []
    for v in retval_vehicles:
        try:
            print('Vehicle: ', v['equipmentID'], 'route: ', route_mapping[str(v['routeID'])])
            listRoute.append(str(v['routeID']))
            listBus.append(v['equipmentID'])
        except Exception as e:
            print(e)
            pass
    return [listRoute, listBus]

if __name__ == '__main__':
    i = 45
    # listBuses = getBusRoute()
    # busDict = {'busID':listBuses[1],'route':listBuses[0], 'timestamp':datetime.now()}
    # with open('route_1509_' + str(i) + '.pickle','wb') as handle:
    #     pickle.dump(busDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    while True:
        print(i)
        # load previous
        with open('route_1509_' + str(i) + '.pickle', 'rb') as handle:
            bus_data = pickle.load(handle)
        l1 = bus_data['busID']

        # get current
        get_bus = getBusRoute()
        if get_bus != None:
            l2 = get_bus[1]
            # compare and save/not save
            if compareList(l1,l2):
                pass
            else:
                print(datetime.now())
                try:
                    data = {'busID':get_bus[1], 'route':get_bus[0], 'timestamp':datetime.now()}
                except Exception as e:
                    print('Error writing new list')
                    print(e)
                    data = {}
                # update i
                i = i + 1
                with open('route_1509_' + str(i) + '.pickle', 'wb') as handle:
                    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            print('error retrieving data from SPOT API...')

        print('going to sleep...')
        t.sleep(300)











