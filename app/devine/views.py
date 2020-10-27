from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .chargepoint import chargepoint_api

def home(request):

    return render(request, 'home.html')

# def db_update_from_chargepoint(self):
    