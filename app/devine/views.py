from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .chargepoint import chargepoint_api as cp
from .optimization import energy_opt
from .models import *
import time
from datetime import datetime, timedelta
from pytz import timezone

def home(request):
    db_update_by_cp()
    db_update_from_opt()
    return render(request, 'home.html')


def db_update_by_cp():
    except_flag, retval_all_groups, retval_act_sessions = cp.read_all_groups()
    if except_flag == False:
        resp_code = retval_all_groups
        resp_text = retval_act_sessions
        alert = db_alert()
        alert.alert_time = timezone.now()
        alert.alert_type = 'ChargePoint API'
        alert.alert_desc = resp_text
        alert.alert_status = 'Open'
        alert.save()

        # TODO: @Zixiong Wait for dicussion to finish handling exception
        # db_opt_session.objects.all().delete()
        # stations = db_station.objects.all()
        # for station in stations:
        #     station
        return

    print('*' * 100)
    start = time.time()
    for retval_one_group in retval_all_groups:
        for retval_one_station in retval_one_group:
            for retval in retval_one_station['Port']:
                # update properties for station
                station = db_station()
                try:
                    station = db_station.objects.get(
                        station_id=retval_one_station['station_id'],
                        port_number=retval['port_number'])
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

                if retval['port_status'] == "INUSE" and retval['user_id'] is not None:
                    # update user
                    user = db_user()
                    try:
                        user = db_user.objects.get(user_id=retval['user_id'])
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

    db_opt_session.objects.all().delete()
    for retval in retval_act_sessions:
        session = db_opt_session()
        session.session_id = retval['sessionID']
        session.group_name = retval['groupName']
        session.start_time = retval['startTime']
        session.timestamp = retval['timestamp']
        session.energy = retval['energy']
        session.user_id = retval['userID']
        session.save()

    print('Total View Time: ', time.time() - start)


def db_update_daily_session_by_cp(request):
    now = timezone.now()
    zeroToday = now - timedelta(
        hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    zeroYesterday = zeroToday - timedelta(hours=24, minutes=0, seconds=0)

    # When dev, you might call this function by accident, so it helps check daily ingestion to avoid duplicate
    isExist = db_ui_session.objects.filter(timestamp__gte=zeroToday)
    if len(isExist) > 0:
        print(len(isExist))
        print("checked duplicate")
        return render(request, 'home.html')

    retvals = cp.read_daily_sessions(zeroYesterday)
    for retval in retvals:
        session = db_ui_session()
        session.session_id = retval['sessionID']
        session.group_name = retval['groupName']
        session.start_time = retval['startTime']
        session.end_time = retval['endTime']
        session.timestamp = retval['timestamp']
        session.energy = retval['energy']
        session.user_id = retval['userID']
        session.save()

    return render(request, 'home.html')


def db_update_from_ui(request):  # TODO: @Yiwen Simply save the four percent params into db
    return render(request, 'home.html')


def db_ingest_config():  # ingest constant information for 5 groups
    sites = [
        ['slac_GISMO', '2575 Sand Hill Road, Menlo Park, CA, 94025', 6.600],
        ['slac_B53', '2575 Sand Hill Road, Menlo Park, CA, 94025', 39.600],
        ['google_CRIT', '1300 Crittenden Ln, Mountain View CA 94043', 376.200],
        ['google_B46', '1565 Charleston Rd, Mountain View CA 94043', 459.200],
        ['google_plymouth', '1625 Plymouth Rd, Mountain View CA 94043', 419.600],
    ]

    for site in sites:
        obj = db_config()
        obj.group_name = site[0]
        obj.address = site[1]
        obj.max_power = site[2]
        obj.save()

def db_update_from_opt():
    groups = ['slac_GISMO', 'slac_B53', 'google_CRIT', 'google_B46', 'google_plymouth']
    
    # Store the max_power configuration for each group
    group_conifg = {}
    # Get the max power configuration for each group
    all_config = db_config.objects.all()
    hour_now = datetime.now().hour
    for config in all_config:
        # Use the day percent from 6 am to 7 pm; 
        # use 100% when user hasn't input any percent for the transformer
        perc = 1.0
        if hour_now >= 6 and hour_now < 19:
            if config.day_perc:
                perc = float(config.day_perc)
        else:
            if config.night_perc:
                perc = float(config.night_perc)
        if config.max_power:
            group_conifg[config.group_name] = float(config.max_power) * perc
    
    # Store the information for sessions with userID=None
    none_user_power = {}
    for group in groups:
        none_user_power[group] = []

    # Store the count for sessions with energy field for further debug
    fail_get_energy_cnt=0
    # Store the charging information to do optimization for each vehicle
    opt_input = {}
    for group in groups:
        opt_input[group] = []

    # Get the charging information from the INUSE ports
    inuse_stations = db_station.objects.filter(port_status='INUSE')
    for inuse_station in inuse_stations:
        # Deal with userID=None
        if inuse_station.recent_user is None:
            tmp_input = {
                'station_id':inuse_station.station_id,
                'port_number':inuse_station.port_number,
                'port_power':inuse_station.port_power,
            }
            none_user_power[inuse_station.group_name].append(tmp_input)
        else:
            tmp_input = {
                    'station_id':inuse_station.station_id,
                    'port_number':inuse_station.port_number,
                    'user_id':inuse_station.recent_user.user_id,
                    'port_power':inuse_station.port_power,
                    'energy': 0.0,
                }
            try:
                session = db_opt_session.objects.get(user_id = inuse_station.recent_user.user_id)
                tmp_input['energy'] = session.energy
            except:
                # Use the default energy=0.0 when no information for energy
                fail_get_energy_cnt+=1
            opt_input[inuse_station.group_name].append(tmp_input)
    
    ret_val = energy_opt(group_conifg, opt_input, none_user_power,fail_get_energy_cnt)
    
    # TODO: @Zixiong Store the return value into the database
