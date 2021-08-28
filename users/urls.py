from django.conf.urls import url
from django.conf.urls import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from . import views

app_name = 'users'

urlpatterns = [
    url(r'^activate/(?P<activationKey>[\w-]+)/$', views.activation_view, name='activation_view'),
    url("address/", views.AddressListView.as_view(), name="address_list", ),
    url("address-create/", views.AddressCreateView.as_view(), name="address_create", ),
    url("automobile-create/", views.AutomobileCreateView.as_view(), name="automobile_create", ),
    url("^address-(?P<pk>[\w-]+)/update/$", views.AddressUpdateView.as_view(), name="address_update", ),
    url('^address-(?P<pk>[\w-]+)/delete/$', views.AddressDeleteView.as_view(), name="address_delete", ),
    url('automobile-register-confirm/',
        TemplateView.as_view(template_name='users/service_providers/automobile_register_confirm.html'),
        name='automobile_confirm'),

    url("^address-(?P<pk>[\w-]+)/update/$", views.AddressUpdateView.as_view(), name="address_update", ),

    url('login/', auth_views.LoginView.as_view(template_name='users/registration/login.html'), name='login'),
    url('logout/', auth_views.LogoutView.as_view(template_name='users/registration/logout.html'), name='logout'),

    url('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='users/registration/password_change.html'), name='password_change'),
    url('password-change-done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='users/registration/password_change_done.html'),
        name='password_change_done'),
    url('personal-info/', views.personal_info, name='personal_info'),
    url('profile/', views.profile, name='profile'),

    url('order-info/', views.order_info, name='order_info'),
    url('order-details/(?P<order_id>[-\w]+)/$', views.order_details, name='order-details'),

    url('register/', views.register, name='register'),
    url('re-order/(?P<order_id>[-\w]+)/$', views.re_order, name='re-order'),


]
