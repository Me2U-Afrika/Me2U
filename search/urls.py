# from django.conf.urls.defaults import *
from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'search'

urlpatterns = [
    url(r'^$', views.search_results, name='search_results'),
    path('autocomplete', views.autocomplete, name='autocomplete')

]
