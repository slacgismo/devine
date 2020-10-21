from django.db import models

# Create your models here.

class user(models.Model):
    user_id = models.CharField(max_length=256,primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_power = models.DecimalField(max_digits=10, decimal_places=2)#assumption

    def __str__(self):
        return self.user_id + ':' + self.user_power + 'kW'

class station(models.Model):
    station_id = models.CharField(max_length=256)
    port_number = models.CharField(max_length=10)
    station_status = models.CharField(max_length=64)
    shed_status = models.BooleanField()
    station_load = models.DecimalField(max_digits=10, decimal_places=2)
    port_load = models.DecimalField(max_digits=10, decimal_places=2)
    allowed_load = models.DecimalField(max_digits=10, decimal_places=2)
    user_obj = models.ForeignKey(user, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together=("station_id","port_number")
    def __str__(self):
        return self.station_id + ' #' + self.port_number + ':' + self.user_id
