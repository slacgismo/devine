from django.db import models

# Create your models here.

class db_user(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=128)
    session_id = models.CharField(max_length=128) 
    timestamp = models.DateTimeField(auto_now_add=True)
    recent_station_id = models.CharField(max_length=256, blank=True)
    recent_port_number = models.CharField(max_length=10, blank=True)
    group_name = models.CharField(max_length=256, default='slac_GISMO')

    def __str__(self):
        return self.user_id + ':' + self.recent_station_id + ' '+self.recent_port_number


class db_station(models.Model):
    station_id = models.CharField(max_length=128)
    group_name = models.CharField(max_length=256)
    station_load = models.DecimalField(max_digits=10, decimal_places=3)
    port_number = models.CharField(max_length=10)
    port_status = models.CharField(max_length=64)
    shed_state = models.BooleanField()
    port_load = models.DecimalField(max_digits=10, decimal_places=3)
    allowed_load = models.DecimalField(max_digits=10, decimal_places=3)
    port_power = models.DecimalField(max_digits=10, decimal_places=3)
    recent_user = models.ForeignKey(db_user, on_delete=models.DO_NOTHING, null=True)
    port_timestamp = models.DateTimeField()
    exception_flag = models.BooleanField(default=False) #0:success 1:exception 

    class Meta:
        unique_together=("station_id","port_number")
    def __str__(self):
        return self.station_id + ' #' + self.port_number + ':' + self.user_id


class db_config(models.Model):# group configs 
    group_name = models.CharField(max_length=256)
    max_power = models.DecimalField(max_digits=10, decimal_places=3)
    day_perc = models.DecimalField(max_digits=10, decimal_places=5, default=0.000)
    night_perc = models.DecimalField(max_digits=10, decimal_places=5, default=0.000)
    yellow_perc = models.DecimalField(max_digits=10, decimal_places=5, default=1.000)
    red_perc = models.DecimalField(max_digits=10, decimal_places=5, default=1.000)
    address = models.CharField(max_length=512)

    def __str__(self):
        return self.group_name + ' : ' + self.max_power + 'kw'


class db_alert(models.Model):#source1: chargepoint API, source2: Django detection 
    alert_time = models.DateTimeField()
    alert_type = models.CharField(max_length=64)
    alert_desc = models.CharField(max_length=256)
    alert_status = models.CharField(max_length=32)

    def __str__(self):
        return self.alert_time + ':' + self.alert_type


class db_ui_session(models.Model):# for UI, every day 
    session_id = models.CharField(max_length=256)
    group_name = models.CharField(max_length=256)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    timestamp = models.DateTimeField()
    energy = models.DecimalField(max_digits=10, decimal_places=3)
    user_id = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.session_id + ',' + self.group_name


class db_opt_session(models.Model):# for optimization, every 5 min 
    #the same with db_ui_session, except for lack of end_time
    session_id = models.CharField(max_length=256)
    group_name = models.CharField(max_length=256)
    start_time = models.DateTimeField()
    timestamp = models.DateTimeField()
    energy = models.DecimalField(max_digits=10, decimal_places=3)
    user_id = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.session_id + ',' + self.group_name


class db_notification(models.Model):
    email = models.CharField(max_length=256)
    yellow_load = models.BooleanField(default=False)
    red_load = models.BooleanField(default=False)
    telecomm_alert = models.BooleanField(default=False)

    def __str__(self):
        return self.email