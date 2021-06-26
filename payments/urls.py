from django.urls import path
from django.contrib import admin

from payments import views

app_name = 'payments'
urlpatterns = [
    path('rave_charge_card/', views.rave_charge_card, name="rave_charge_card"),
]
