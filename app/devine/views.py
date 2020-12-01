from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .chargepoint import chargepoint_api as cp
from .models import *
import time
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
from django.core.serializers.json import DjangoJSONEncoder
import json
from rest_framework.views import APIView

#TODO: add enough error handlers to each functions
#TODO: when connecting with frontend, all the request.POST/request.GET should be replaced by request.data/request.query_params.get

def home(request):
    # db_update_by_cp()
    request.method = 'GET'
    request.GET._mutable = True
    request.GET['group_name'] = 'slac_GISMO'
    getAlerts().get(request)
    return render(request, 'home.html')


def db_update_by_cp():
    except_flag, ret_val_all_groups, ret_val_act_sessions = cp.read_all_groups()
    if except_flag == False:
        resp_code = ret_val_all_groups
        resp_text = ret_val_act_sessions
        alert = db_alert()
        alert.alert_time = timezone.now()
        alert.alert_type = 'ChargePoint API'
        alert.alert_desc = resp_text
        alert.alert_status = 'Open'
        #FIXME: Now the alert save every error message to a default group 'slac_GISMO'. In future, we should design
        # a proper way to save and show the alerts, no matter split by group or share as public
        alert.save()

        return

    print('*' * 100)
    start = time.time()
    for ret_val_one_group in ret_val_all_groups:
        for ret_val_one_station in ret_val_one_group:
            for ret_val in ret_val_one_station['Port']:
                # update properties for station
                station = db_station()
                try:
                    station = db_station.objects.get(
                        station_id=ret_val_one_station['station_id'],
                        port_number=ret_val['port_number'])
                except:
                    # print("new station")
                    station.station_id = ret_val_one_station['station_id']
                    station.port_number = ret_val['port_number']
                station.group_name = ret_val_one_station['group_name']
                station.station_load = ret_val_one_station['station_load']

                # update properties for ports
                station.port_status = ret_val['port_status']
                station.shed_state = ret_val['shed_state']
                station.port_load = ret_val['port_load']
                station.allowed_load = ret_val['allowed_load']
                station.port_power = ret_val['port_power']
                station.recent_user = None
                station.port_timestamp = ret_val['port_timestamp']

                if ret_val['port_status'] == "INUSE" and ret_val['user_id'] is not None:
                    # update user
                    user = db_user()
                    try:
                        user = db_user.objects.get(user_id=ret_val['user_id'])
                    except:
                        print("new user")
                        user.user_id = ret_val['user_id']

                    # update recent use for ports
                    user.recent_station_id = ret_val_one_station['station_id']
                    user.session_id = str(ret_val['session_id'])
                    user.recent_port_number = ret_val['port_number']
                    user.timestamp = ret_val['port_timestamp']
                    user.save()

                    #add foreign user key
                    station.recent_user = user

                station.save()

    db_opt_session.objects.all().delete()
    for ret_val in ret_val_act_sessions:
        session = db_opt_session()
        session.session_id = ret_val['sessionID']
        session.group_name = ret_val['groupName']
        session.start_time = ret_val['startTime']
        session.timestamp = ret_val['timestamp']
        session.energy = ret_val['energy']
        session.user_id = ret_val['userID']
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

    ret_vals = cp.read_daily_sessions(zeroYesterday)
    for ret_val in ret_vals:
        session = db_ui_session()
        session.session_id = ret_val['sessionID']
        session.group_name = ret_val['groupName']
        session.start_time = ret_val['startTime']
        session.end_time = ret_val['endTime']
        session.timestamp = ret_val['timestamp']
        session.energy = ret_val['energy']
        session.user_id = ret_val['userID']
        session.save()

    return render(request, 'home.html')


# manually ingestion
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

class getUniqueDriversByDate(APIView): 
    def get(self, request):
        nows = timezone.now()
        zero_today = nows - timedelta(
            hours=nows.hour, minutes=nows.minute, seconds=nows.second, microseconds=nows.microsecond)
        zero_seventh_day = zero_today - timedelta(hours=24*7, minutes=0, seconds=0)
        zero_sixth_day = zero_today - timedelta(hours=24*6, minutes=0, seconds=0)
        zero_fifth_day = zero_today - timedelta(hours=24*5, minutes=0, seconds=0)
        zero_fourth_day = zero_today - timedelta(hours=24*4, minutes=0, seconds=0)
        zero_third_day = zero_today - timedelta(hours=24*3, minutes=0, seconds=0)
        zero_second_day = zero_today - timedelta(hours=24*2, minutes=0, seconds=0)
        zero_first_day = zero_today - timedelta(hours=24*1, minutes=0, seconds=0)

        seventh_day = db_user.objects.filter(group_name=request.GET['group_name']).filter(timestamp__gte=zero_seventh_day).filter(timestamp__lte=zero_sixth_day)
        sixth_day = db_user.objects.filter(group_name=request.GET['group_name']).filter(timestamp__gte=zero_sixth_day).filter(timestamp__lte=zero_fifth_day)
        fifth_day = db_user.objects.filter(group_name=request.GET['group_name']).filter(timestamp__gte=zero_fifth_day).filter(timestamp__lte=zero_fourth_day)
        fourth_day = db_user.objects.filter(group_name=request.GET['group_name']).filter(timestamp__gte=zero_fourth_day).filter(timestamp__lte=zero_third_day)
        third_day = db_user.objects.filter(group_name=request.GET['group_name']).filter(timestamp__gte=zero_third_day).filter(timestamp__lte=zero_second_day)
        second_day = db_user.objects.filter(group_name=request.GET['group_name']).filter(timestamp__gte=zero_second_day).filter(timestamp__lte=zero_first_day)
        first_day = db_user.objects.filter(group_name=request.GET['group_name']).filter(timestamp__gte=zero_first_day).filter(timestamp__lte=zero_today)

        context={
            'date':[str(zero_seventh_day.month)+'/'+str(zero_seventh_day.day),
                    str(zero_sixth_day.month)+'/'+str(zero_sixth_day.day),
                    str(zero_fifth_day.month)+'/'+str(zero_fifth_day.day),
                    str(zero_fourth_day.month)+'/'+str(zero_fourth_day.day),
                    str(zero_third_day.month)+'/'+str(zero_third_day.day),
                    str(zero_second_day.month)+'/'+str(zero_second_day.day),
                    str(zero_first_day.month)+'/'+str(zero_first_day.day)],
            'number_of_unique_drivers':[len(seventh_day), len(sixth_day), len(fifth_day), 
                    len(fourth_day), len(third_day),len(second_day),len(first_day)]
        }
        # print(context)
        response_json = json.dumps(context,cls=DjangoJSONEncoder)
        response = HttpResponse(response_json, content_type='application/json')
        return response


class getAlerts(APIView): 
    def get(self, request):
        alerts = db_alert.objects.filter(group_name=request.GET['group_name'])
        context={
            'date':[],
            'time':[],
            'type':[],
            'description':[],
            'status':[]
        }
        for alert in alerts:
            context['date'].append(str(alert.alert_time.date()))
            context['time'].append(alert.alert_time.time().strftime('%H:%M:%S'))
            context['type'].append(alert.alert_type)
            context['description'].append(alert.alert_desc)
            context['status'].append(alert.alert_status)
        # print(context)
        response_json = json.dumps(context,cls=DjangoJSONEncoder)
        response = HttpResponse(response_json, content_type='application/json')
        return response