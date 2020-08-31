from django.conf.urls import url
from django.conf.urls import *
from django.views.generic import TemplateView

from . import views

app_name = 'users'

urlpatterns = [
    # url(r'^$', views.index),
    url('register/', views.register, name='register'),
    # url('register_seller/', views.register_seller, name='register_seller'),
    # url('/signup/', views.seller_register.SignUpView.as_view(), name='signup'),
    url('profile/', views.profile, name='profile'),
    url('order-info/', views.order_info, name='order-info'),
    url('personal-info/', views.personal_info, name='personal-info'),
    url('order-details/(?P<order_id>[-\w]+)/$', views.order_details, name='order-details'),
    url('re-order/(?P<order_id>[-\w]+)/$', views.re_order, name='re-order'),
    url("address/", views.AddressListView.as_view(), name="address_list", ),
    url("address-create/", views.AddressCreateView.as_view(), name="address_create", ),
    url("automobile-create/", views.AutomobileCreateView.as_view(), name="automobile_create", ),
    url("seller-create/", views.SellerCreateView.as_view(), name="seller_create", ),
    url("^address-(?P<pk>[\w-]+)/update/$", views.AddressUpdateView.as_view(), name="address_update", ),
    url('^address-(?P<pk>[\w-]+)/delete/$', views.AddressDeleteView.as_view(), name="address_delete", ),
    url('automobile-register-confirm/',
            TemplateView.as_view(template_name='users/service_providers/automobile_register_confirm.html'),
            name='automobile_confirm'),
    url('seller-register-confirm/',
                TemplateView.as_view(template_name='users/service_providers/seller_register_confirm.html'),
                name='seller_confirm'),

]
