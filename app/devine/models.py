from django.db import models

# Create your models here.

class user(models.Model):
    user_id = models.CharField(max_length=256,primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # user_power = models.DecimalField(max_digits=10, decimal_places=2)#assumption TODO
    recent_station_id = models.CharField(max_length=256, blank=True)
    recent_port_number = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.user_id + ':' + self.recent_station_id + ' '+self.recent_port_number

class station(models.Model):
    station_id = models.CharField(max_length=256)
    station_load = models.DecimalField(max_digits=10, decimal_places=2)
    port_number = models.CharField(max_length=10)
    port_status = models.CharField(max_length=64)
    shed_state = models.BooleanField()
    port_load = models.DecimalField(max_digits=10, decimal_places=2)
    allowed_load = models.DecimalField(max_digits=10, decimal_places=2)
    port_power = models.DecimalField(max_digits=10, decimal_places=2,blank=True,default="")
    recent_user = models.ForeignKey(user, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together=("station_id","port_number")
    def __str__(self):
        return self.station_id + ' #' + self.port_number + ':' + self.user_id
