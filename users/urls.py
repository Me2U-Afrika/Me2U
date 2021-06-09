from django.conf.urls import url
from django.conf.urls import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views



from . import views

app_name = 'users'

urlpatterns = [
    # url(r'^$', views.index),
    url('register/', views.register, name='register'),
    # url('register_seller/', views.register_seller, name='register_seller'),
    # url('/signup/', views.seller_register.SignUpView.as_view(), name='signup'),
    url('profile/', views.profile, name='profile'),
    url('order-info/', views.order_info, name='order_info'),
    url('personal-info/', views.personal_info, name='personal_info'),
    url('order-details/(?P<order_id>[-\w]+)/$', views.order_details, name='order-details'),
    url('re-order/(?P<order_id>[-\w]+)/$', views.re_order, name='re-order'),
    url("address/", views.AddressListView.as_view(), name="address_list", ),
    url("address-create/", views.AddressCreateView.as_view(), name="address_create", ),
    url("automobile-create/", views.AutomobileCreateView.as_view(), name="automobile_create", ),
    url("seller-create/", views.SellerCreateView.as_view(), name="seller_create", ),
    url("brand-create/", views.BrandCreateView.as_view(), name="brand_create", ),
    url(r'^brand-(?P<pk>[\w-]+)/update/$', views.BrandUpdateView.as_view(),
        name="brand_update"),
    url("^address-(?P<pk>[\w-]+)/update/$", views.AddressUpdateView.as_view(), name="address_update", ),
    url('^address-(?P<pk>[\w-]+)/delete/$', views.AddressDeleteView.as_view(), name="address_delete", ),
    url('automobile-register-confirm/',
            TemplateView.as_view(template_name='users/service_providers/automobile_register_confirm.html'),
            name='automobile_confirm'),
    # url('seller-register-confirm/',
    #             TemplateView.as_view(template_name='users/service_providers/seller_register_confirm.html'),
    #             name='seller_confirm'),

    url("^address-(?P<pk>[\w-]+)/update/$", views.AddressUpdateView.as_view(), name="address_update", ),

                
    url(r'^activate/(?P<activationKey>[\w-]+)/$', views.activation_view, name='activation_view'),
    url('login/', auth_views.LoginView.as_view(template_name='users/registration/login.html'), name='login'),
    # url('login/', views.Login, name='login'),
    url('logout/', auth_views.LogoutView.as_view(template_name='users/registration/logout.html'), name='logout'),
    url('password-change/', auth_views.PasswordChangeView.as_view(template_name='users/registration/password_change'
                                                                                '.html'),
        name='password_change'),
    url('password-change-done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='users/registration/password_change_done.html'),
        name='password_change_done'),

]
