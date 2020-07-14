from django.conf.urls import url
from . import views
app_name = 'users'

urlpatterns = [
    # url(r'^$', views.index),
    url('register/', views.register, name='register'),
    url('profile/', views.profile, name='profile'),
    url('order-info/', views.order_info, name='order-info'),
    url('order-details/(?P<order_id>[-\w]+)/$', views.order_details, name='order-details'),
    url('re-order/(?P<order_id>[-\w]+)/$', views.re_order, name='re-order'),

]
