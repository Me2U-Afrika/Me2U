from django.contrib import admin
from datetime import datetime, timedelta
import logging
from . import models
from .models import Profile, User, SellerProfile, AutomobileProfile
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.db.models.functions import TruncDay
from django.db.models import Avg, Count, Min, Sum
from django.urls import path
from django.template.response import TemplateResponse

from . import models
from me2ushop.admin import main_admin

logger = logging.getLogger(__name__)


# Register your models here.
@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined")},
        ),
    )
    add_fieldsets = (
        (None,
         {
             "classes": ("wide",),
             "fields": ("username", "email", "password1", "password2"),
         },
         ),
    )
    list_display = (
        'username',
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )
    search_fields = ('username', "email", "first_name", "last_name")
    list_display_links = ("email",)
    ordering = ("date_joined",)

# class SellerAdmin(models.Admin):
#     list_display = ('')



admin.site.register(Profile)
# main_admin.register(Profile)
# main_admin.register(User, UserAdmin)

# main_admin.register(SellerProfile)
admin.site.register(SellerProfile)

admin.site.register(AutomobileProfile)
# main_admin.register(AutomobileProfile)

