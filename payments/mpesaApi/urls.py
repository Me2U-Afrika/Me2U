from django.urls import path
from django.contrib import admin

from payments.mpesaApi.views import LNMCallbackAPIView
urlpatterns = [
    path('lnm/', LNMCallbackAPIView.as_view(), name="lnm_callbackurl"),
]
