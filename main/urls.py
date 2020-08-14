from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

app_name = 'main'

urlpatterns = [
    # url(r'^$', views.index),
    url(r'^$', views.welcome, name='homepage'),
    url('aboutus/', TemplateView.as_view(template_name='about_us.html'), name='aboutus'),
    url('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    url('ourdrivers/', views.our_drivers, name='ourdrivers'),
    url('add_to_cart/', views.add_to_cart, name='add_to_cart'),

]
