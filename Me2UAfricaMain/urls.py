from django.conf.urls import url
from . import views

# app_name = 'me2shop'
urlpatterns = [
    # url(r'^$', views.index),
    url(r'^$', views.welcome, name='homepage'),
    url('aboutus/', views.aboutus, name='aboutus'),
    url('ourdrivers/', views.our_drivers, name='ourdrivers'),


]
