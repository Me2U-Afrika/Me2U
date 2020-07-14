from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from . import views

app_name = 'categories'

urlpatterns = [
    url(r'^$', views.categoriesHomePage, name='categoriesHome'),
    url(r'^categoryView/(?P<slug>[\w-]+)/$', views.CategoryDetailedView.as_view(), name='categoryView'),
    url(r'^categoryView_africa_made/(?P<slug>[\w-]+)/$', views.CategoryDetailedView_africa_made.as_view(), name='categoryView_africa_made'),

    url('get_products/$', views.get_json_products, name='get_products'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
