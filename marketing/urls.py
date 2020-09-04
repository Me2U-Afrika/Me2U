import django
from django.conf.urls import url
from django.urls import path
from marketing.sitemap import SITEMAPS
from . import views
from django.contrib.sitemaps import views as view

app_name = 'marketing'

urlpatterns = [
    url(r'^robots/', views.robots),

]

urlpatterns += url(r'^sitemap\.xml$', view.sitemap, {'sitemaps': SITEMAPS}),
