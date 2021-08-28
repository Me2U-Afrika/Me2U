"""Me2U URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.main, name='main')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='main')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from me2ushop import admin as main_admin

from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
import certbot_django.server.urls

from me2ushop.views import TransactionDetailView

urlpatterns = [
    url('', include('me2ushop.urls')),
    # cerbot
    url(r'^\.well-known/', include(certbot_django.server.urls)),

    path('accounts/', include('allauth.urls')),
    path('api-auth', include('rest_framework.urls')),
    path('api/payments/', include('payments.mpesaApi.urls')),

    url(r'^blog/', include('blog.urls')),

    url(r'^currencies/', include('currencies.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    # url(r'^cache/', include('django_memcached.urls')),
    url('categories', include('categories.urls', namespace='categories')),

    url(r'^dispatch-admin/', main_admin.dispatchers_admin.urls),
    path("djangorave/<str:reference>/", TransactionDetailView.as_view(), name="reference"),
    path("djangorave/", include("djangorave.urls", namespace="djangorave")),

    url(r'^main-admin/', admin.site.urls),
    url('main/', include('main.urls')),
    url('marketing/', include('marketing.urls')),

    url(r'^office-admin/', main_admin.central_office_admin.urls),

    path('payments/', include('payments.urls')),

    url(r'^search/', include('search.urls')),
    url(r'^sellers/', include('sellers.urls')),
    url(r'^seller-admin/', main_admin.sellers_admin.urls),

    url(r'^users/', include('users.urls')),
    url(r'^users/', include('django.contrib.auth.urls')),






]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        url('__debug__/', include(debug_toolbar.urls))
    ]
