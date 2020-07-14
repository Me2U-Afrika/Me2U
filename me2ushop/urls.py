from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

app_name = 'me2ushop'

urlpatterns = [
    url(r'^$', views.homeView, name='home'),
    # url(r'^$', views.HomeView.as_view(), name='home'),

    url('add_cart/(?P<slug>[\w-]+)/$', views.add_cart, name='add_cart'),
    url('remove_cart/(?P<slug>[\w-]+)/$', views.remove_cart, name='remove_cart'),
    url('remove_single_item_cart/(?P<slug>[\w-]+)/$', views.remove_single_item_cart, name='remove_single_item_cart'),

    url('product/(?P<slug>[\w-]+)/$', views.show_product, name='product'),
    url('order_summary/', views.Order_summary_view.as_view(), name='order_summary'),

    url('checkout/', views.Checkout_page.as_view(), name='checkout'),
    url('add_coupon/', views.add_coupon, name='add_coupon'),

    url('payment/(?P<payment_option>[\w-]+)/$', views.PaymentView.as_view(), name='payment'),
    url('request_refund/', views.RefundView.as_view(), name='request_refund'),
    url('add/review', views.add_review),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
