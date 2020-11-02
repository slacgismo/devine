from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .chargepoint import chargepoint_api as cp
from .models import db_user, db_station

def home(request):
    db_update_from_chargepoint()
    
    return render(request, 'home.html')

def db_update_from_chargepoint():
    retvals_all_groups = cp.read_from_sites()
    print('+'*100)
    for retvals_one_group in retvals_all_groups:
        for retval_one_station in retvals_one_group:
            print(retval_one_station)
            # print(retval_one_station[0]['Port'])

            for retval in retval_one_station['Port']:
                # update properties for station
                station = db_station()
                try:
                    station = db_station.objects.get(station_id = retval_one_station['station_id'], port_number = retval['port_number'])
                except:
                    print("new station")
                    station.station_id = retval_one_station['station_id']
                    station.port_number = retval['port_number']
                
                station.station_load = retval_one_station['station_load']   
                # update properties for ports
                station.port_status = retval['port_status']
                station.shed_state = retval['shed_state']
                station.port_load = retval['port_load']
                station.allowed_load = retval['allowed_load']
                station.port_power = retval['port_power']
                station.port_timestamp = retval['port_timestamp']
                #TODO: update user
                
                station.save()
                print(1/0)

    