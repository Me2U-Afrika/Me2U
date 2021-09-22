from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.urls import path, include
from rest_framework import routers
from me2ushop import endpoints
from rest_framework.authtoken import views as authtoken_views
from . import views
from django.views.decorators.cache import cache_page

router = routers.DefaultRouter()
router.register(r'orderitems', endpoints.PaidOrderItemsViewSet)
router.register(r'orders', endpoints.PaidOrderViewSet)

app_name = 'me2ushop'

urlpatterns = [

    # url(r'^$', cache_page(60 * 4)(views.HomeView.as_view()), name='home'),
    url(r'^$', views.HomeViewTemplateView.as_view(), name='home'),
    # url(r'^$', cache_page(60 * 4)(views.HomeViewTemplateView.as_view()), name='home'),
    url(r'^add_cart/(?P<slug>[\w-]+)/$', views.add_cart, name='add_cart'),
    url(r'^add-wishlist/(?P<slug>[\w-]+)/$', views.add_wishlist, name='add_wishlist'),
    url(r'^add/review', views.add_review),
    url(r'^add/tag/', views.add_tag),
    url(r'^color/ajax/', views.colorAjax, name='color_ajax'),
    url(r'^add_coupon/', views.add_coupon, name='add_coupon'),
    url(r'^address_select/', views.AddressSelectionView.as_view(), name='address_select'),

    url(r"^brand-create/", views.BrandCreateView.as_view(), name="brand_create", ),
    url(r"^brand-(?P<pk>[\w-]+)/update/$", views.BrandUpdateView.as_view(), name="brand_update", ),
    url(r'^brand/(?P<slug>[\w-]+)/$', views.SellerView.as_view(), name='seller_page'),
    path('brand-pay/<int:brand_id>/', views.brand_subscription, name="brand_payment"),

    url(r'^customer-service/(?P<order_id>[-\w]+)/$', views.room, name="cs_chat"),
    url(r'^customer-service/', TemplateView.as_view(template_name='customer_service.html'),
        name="cs_main"),
    url(r'^checkout/', views.Checkout_page.as_view(), {'SSL': True}, name='checkout'),
    url(r'^checkout-done/', views.checkout_done, name='checkout-done'),
    url(r'complete/', views.paypal_payment_complete, name='complete'),
    url(r'complete-cart/', views.paypal_payment_complete_cart, name='complete-cart'),


    path("flutter-payment/<str:reference>/", views.flutterCompleteTrans, name="flutter_checkout"),
    url(r'^full-catalog/', views.ProductListView.as_view(), name='full_catalog'),

    url("invoice-cs/(?P<order_id>[\w-]+)/$", views.invoice_for_order, name="invoice_cs", ),

    path('mobile-api/', include(router.urls)),
    path('mobile-api/auth/', authtoken_views.obtain_auth_token, name='mobile_token'),
    path('mobile-api/my-orders/', endpoints.my_orders, name='mobile_my_orders', ),

    url(r'^new-product/(?P<pk>[-\w]+)/$', views.ProductCreateView.as_view(), name='product-create'),

    url(r'^order_summary/', views.Order_summary_view.as_view(), name='order_summary'),
    url(r'^order_dashboard/', views.OrderView.as_view(), name='order_dashboard'),
    # url('order-details/(?P<order_id>[-\w]+)/$', views.refund_status, name='order-details'),

    # url(r'^product/(?P<slug>[\w-]+)/$', cache_page(60 * 8)(views.ProductDetailedView.as_view()), name='product'),
    url(r'^product/(?P<slug>[\w-]+)/$', views.ProductDetailedView.as_view(), name='product'),
    url(r'^product-attributes/(?P<slug>[\w-]+)/create$', views.ProductAttributesCreateView.as_view(),
        name='product_attributes_create'),
    url(r'^product-attribute-(?P<pk>[\w-]+)/update/$', views.ProductAttributeUpdateView.as_view(),
        name="product_update_attributes"),
    url(r'^product-attribute-(?P<pk>[\w-]+)/delete$', views.ProductAttributeDeleteView.as_view(),
        name='product_delete_attributes'),
    url(r'^product-additional-info/(?P<slug>[\w-]+)/update$', views.ProductUpdateAdditionalInforView.as_view(),
        name='product-update-additional-info'),
    url(r'^product/(?P<slug>[\w-]+)/update$', views.ProductUpdateView.as_view(), name='product-update'),
    url(r'^product/(?P<slug>[\w-]+)/delete$', views.ProductDeleteView.as_view(), name='product-delete'),
    url(r"^product-images/(?P<slug>[\w-]+)/$", views.show_product_image, name="product_images", ),
    url(r'^product-images/(?P<slug>[\w-]+)/create$', views.ProductImageCreateView.as_view(),
        name='product_image_create'),
    # url(r'^product-images/(?P<slug>[\w-]+)/create$', views.product_image_create, name='product_image_create'),
    url("^product-image-(?P<pk>[\w-]+)/update/$", views.ProductImageUpdateView.as_view(), name="product_image_update"),
    # url('^image-(?P<pk>[\w-]+)/delete/$', views.ProductImageDeleteView.as_view(), name="product_image_delete"),
    url('^product-image-(?P<pk>[\w-]+)/delete/$', views.delete_image, name="product_image_delete"),
    url(r'payment/(?P<payment_option>[\w-]+)/$', views.PaymentView.as_view(), {'SSL': True}, name='payment'),
    # path('product-add/', views.productAdd, name='product_add', ),

    url(r'^remove_cart/(?P<slug>[\w-]+)/$', views.remove_cart, name='remove_cart'),
    url(r'^remove_single_item_cart/(?P<slug>[\w-]+)/$', views.remove_single_item_cart, name='remove_single_item_cart'),
    # url(r'^refund-status/(?P<order_id>[\w-]+)', views.refund_status, name='refund_status'),
    url('request_refund/', views.RefundView.as_view(), name='request_refund'),

    url('tag/(?P<tag>[\w-]+)/$', views.tag),
    url('tag_cloud', views.tag_cloud, name='tag_cloud'),

    url(r'^wishlist/', views.WishListView.as_view(), name='wish_list'),
    url(r'^wishlist-summary/', views.WishList_Summary.as_view(), name='wishlist_summary'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
