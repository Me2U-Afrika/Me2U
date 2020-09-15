from django.contrib import admin
from .models import Category
from datetime import datetime, timedelta
import logging
from . import models
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.db.models.functions import TruncDay
from django.db.models import Avg, Count, Min, Sum
from django.urls import path
from django.template.response import TemplateResponse

from . import models
from me2ushop import admin as admin_register


logger = logging.getLogger(__name__)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'description', 'is_active', 'created_at', 'updated_at',)
    list_display_links = ('category_name',)
    list_per_page = 20
    ordering = ['category_name']
    search_fields = ['name', 'description', 'meta_keywords', 'meta_description']
    exclude = ('created_at',
               'updated_at',)
    # sets up slug to be generated from category name
    prepopulated_fields = {'slug': ('category_name',)}

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ['slug', 'category_name']

    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}


# main_admin = OwnersAdminSite()

admin.site.register(Category, CategoryAdmin)
admin_register.main_admin.register(Category, CategoryAdmin)
