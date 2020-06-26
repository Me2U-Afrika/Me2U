"""Me2U URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.Me2UAfricaMain, name='Me2UAfricaMain')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='Me2UAfricaMain')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('Me2UAfricaMain/', include('Me2UAfricaMain.urls')),
    url('register/', include('users.urls')),
    url('me2ushop/', include('me2ushop.urls', namespace='me2ushop')),

    url('categories/', include('categories.urls', namespace='categories')),
    # url(r'^cart/', include('cart.urls')),

    url('swiftsuppliers', include('swiftsuppliers.urls')),
    url('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    url('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),


]
