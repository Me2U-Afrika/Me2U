from django.contrib import admin
import logging
from .models import Profile, AutomobileProfile, EmailConfirmed
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from . import models

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


admin.site.register(Profile)
admin.site.register(AutomobileProfile)
admin.site.register(EmailConfirmed)
