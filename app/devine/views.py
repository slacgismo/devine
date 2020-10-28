from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .chargepoint import chargepoint_api as cp
from .models import db_user, db_station

def home(request):
    db_update_from_chargepoint()
    
    return render(request, 'home.html')

def db_update_from_chargepoint():
    retvals = cp.read_from_sites()
    print('+'*100)
    for retval in retvals:
        print(retval[0]['Port'])
        print(len(retval[0]['Port']))
        for i in range(len(retval['Port'])): 
            # update properties for station
            station = db_station()
            try:
                station = db_station.objects.get(station_id = retval['station_id'], port_number = retval['Port'][i]['port_number'])
            except:
                print("new station")
                station.station_id = retval['station_id']
                station.port_number = retval['Port'][i]['port_number']
            
            station.station_load = retval['station_load']   
            # update properties for ports
            station.port_status = retval['Port'][i]['port_status']
            station.shed_state = retval['Port'][i]['shed_state']
            station.port_load = retval['Port'][i]['port_load']
            station.allowed_load = retval['Port'][i]['allowed_load']
            station.port_power = retval['Port'][i]['port_power']
            #TODO: update user
            
            station.save()


    