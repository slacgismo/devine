from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('daily_session',views.db_update_daily_session_by_cp)
]