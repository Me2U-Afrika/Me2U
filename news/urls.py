from django.conf.urls import url
from . import views

# app_name = 'me2shop'
urlpatterns = [
    # url(r'^$', views.index),
    url(r'^$', views.welcome, name='homepage'),
    url('aboutus/', views.aboutus, name='aboutus'),
    url('newsoftoday/', views.news_of_day, name='newsoftoday'),

    # adding dynamic url

    url(r'^archive/(\d{4}-\d{2}-\d{2})/$', views.past_days_news)

]
