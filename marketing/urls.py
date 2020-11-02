import django
from django.conf.urls import url
from django.urls import path
from marketing.sitemap import SITEMAPS
from . import views
from django.contrib.sitemaps import views as view

app_name = 'marketing'

urlpatterns = [
    url(r'^robots/', views.robots),
    url(r'^ajax/email-signup/', views.email_signup, name="ajax_email_signup"),

]

urlpatterns += url(r'^sitemap\.xml$', view.sitemap, {'sitemaps': SITEMAPS}),
