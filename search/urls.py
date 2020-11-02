# from django.conf.urls.defaults import *
from django.conf.urls import url
from . import views

app_name = 'search'

urlpatterns = [
    url(r'^$', views.search_results, name='search_results'),

]
