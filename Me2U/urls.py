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
from me2ushop import admin as main_admin

from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^main-admin/', admin.site.urls),
    url(r'^office-admin/', main_admin.central_office_admin.urls),
    url(r'^seller-admin/', main_admin.sellers_admin.urls),
    url(r'^dispatch-admin/', main_admin.dispatchers_admin.urls),

    path('api-auth', include('rest_framework.urls'), ),

    url('main/', include('main.urls')),
    url('users/', include('users.urls')),
    url('users/', include('django.contrib.auth.urls')),

    url('search/', include('search.urls')),
    url('sellers/', include('sellers.urls')),

    url('', include('me2ushop.urls')),
    url('marketing/', include('marketing.urls')),

    url('categories', include('categories.urls', namespace='categories')),

    # url('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # url('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    # url('password-change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change.html'),
    #     name='password-change'),
    # url('password_change_done/',
    #     auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
    #     name='password_change_done'),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        url('__debug__/', include(debug_toolbar.urls))
    ]
