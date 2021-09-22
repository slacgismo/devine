
import requests
import config
import pandas as pd
import pickle

# configuration
baseURL = config.baseURL
endURL = config.endURL

def updateRouteMapping():
    service = 'get_routes'
    resp = requests.get(url=baseURL+service+endURL)
    retval_routes = resp.json()[service]

    list_routeID = []
    list_routeName = []
    dict_map = {}
    for i in retval_routes:
        list_routeName.append(i['name'])
        list_routeID.append(i['id'])
        dict_map[str(i['id'])] = i['name']
    # dict_map = {'route_id':list_routeID, 'route_name':list_routeName}
    with open('routeMapping.pickle','wb') as handle:
        pickle.dump(dict_map, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return dict_map

#TODO: Figure out this methid and what to generate
def updateVehiclesList():
    service = 'get_vehicles'
    resp = requests.get(url=baseURL + service + endURL)
    retval_vehicles = resp.json()[service]
    vehiclesID = []
    for v in retval_vehicles:
        vehiclesID.append(v['equipmentID'])

if __name__ == '__main__':
    # map = updateRouteMapping()
    service = 'get_schedules'
    resp = requests.get(url=baseURL + service + endURL)
    retval_vehicles = resp.json()[service]