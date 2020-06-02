from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.index),
    url(r'^$', views.register, name='register'),
    url('profile/', views.profile, name='profile'),

]
