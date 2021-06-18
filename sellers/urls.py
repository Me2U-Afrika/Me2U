from django.conf.urls import url
from django.urls import path

from . import views
from django.views.generic import TemplateView

app_name = 'sellers'

urlpatterns = [
    # url(r'sellers/', views.seller_page, name='seller_home'),
    # url('^(?P<brand_id>[-\w]+)/$', views.seller_page, name='seller_home'),
    url(r'^brand/(?P<slug>[\w-]+)/$', views.seller_page, name='seller_home'),

    # url('customer-details/(?P<id>[-\w]+)/$', views.customer_details, name='customer_details'),
    path('customer-details/<str:id>', views.customer_details, name='customer_details'),
    path('customer-address/<str:id>', views.customer_address, name='customer_address'),
    url('my-products/(?P<brand_id>[-\w]+)/$', views.seller_products, name='seller_products'),

    # url('aboutus/', TemplateView.as_view(template_name='about_us.html'), name='aboutus'),
    # url('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    # url('ourdrivers/', views.our_drivers, name='ourdrivers'),
    # url('add_to_cart/', views.add_to_cart, name='add_to_cart'),

]
