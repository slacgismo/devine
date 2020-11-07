from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .chargepoint import chargepoint_api as cp
from .models import *
import time
from datetime import datetime

def home(request):
    db_update_from_chargepoint()
    
    return render(request, 'home.html')

def db_update_from_chargepoint():
    retval_all_groups, retval_act_sessions = cp.readAllGroups()
    print('*'*100)
    start = time.time()
    for retval_one_group in retval_all_groups:
        for retval_one_station in retval_one_group:
            for retval in retval_one_station['Port']:
                # update properties for station
                station = db_station()
                try:
                    station = db_station.objects.get(station_id = retval_one_station['station_id'], port_number = retval['port_number'])
                except:
                    # print("new station")
                    station.station_id = retval_one_station['station_id']
                    station.port_number = retval['port_number']
                station.group_name = retval_one_station['group_name']
                station.station_load = retval_one_station['station_load']   

                # update properties for ports
                station.port_status = retval['port_status']
                station.shed_state = retval['shed_state']
                station.port_load = retval['port_load']
                station.allowed_load = retval['allowed_load']
                station.port_power = retval['port_power']
                station.recent_user = None
                station.port_timestamp = retval['port_timestamp']
                
                if retval['port_status']=="INUSE" and retval['user_id'] is not None:
                    # update user
                    # print('so:'+retval['user_id'])
                    user = db_user()
                    # if retval['user_id'] is None:
                    #     user.user_id = 'None'+ str(retval['session_id'])
                    # else:
                    try:
                        user = db_user.objects.get(user_id = retval['user_id'])
                    except:
                        print("new user")
                        user.user_id = retval['user_id']
                    
                    # update recent use for ports
                    user.recent_station_id = retval_one_station['station_id']
                    user.session_id = str(retval['session_id'])
                    user.recent_port_number = retval['port_number']
                    user.timestamp = retval['port_timestamp']
                    user.save()
                    
                    #add foreign user key
                    station.recent_user = user

                station.save()
    
    for retval in retval_act_sessions:
        session = db_opt_session()
        session.session_id = retval['sessionID']
        session.group_name = retval['groupName']
        session.start_time = retval['startTime']
        session.timestamp = retval['timestamp']
        session.energy = retval['energy']
        session.user_id = retval['userID']
        session.save()

    print('Total Time: ', time.time()-start)

    