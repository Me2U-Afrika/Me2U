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

    # url('categoryView/(?P<slug>[\w-]+)/$', views.CategoryDetailedView, name='categoryView'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
