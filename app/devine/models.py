from django.db import models

# Create your models here.

class db_user(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)
    recent_station_id = models.CharField(max_length=256, blank=True)
    recent_port_number = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.user_id + ':' + self.recent_station_id + ' '+self.recent_port_number

class db_station(models.Model):
    station_id = models.CharField(max_length=256)
    station_load = models.DecimalField(max_digits=10, decimal_places=3)
    port_number = models.CharField(max_length=10)
    port_status = models.CharField(max_length=64)
    shed_state = models.BooleanField()
    port_load = models.DecimalField(max_digits=10, decimal_places=3)
    allowed_load = models.DecimalField(max_digits=10, decimal_places=3)
    port_power = models.DecimalField(max_digits=10, decimal_places=3,blank=True,default="")
    recent_user = models.ForeignKey(db_user, on_delete=models.DO_NOTHING, null=True)
    port_timestamp = models.DateTimeField(null=True)

    class Meta:
        unique_together=("station_id","port_number")
    def __str__(self):
        return self.station_id + ' #' + self.port_number + ':' + self.user_id