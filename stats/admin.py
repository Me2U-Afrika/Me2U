from django.contrib import admin
from .models import PageView, ProductView


# Register your models here.

class TrackingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'product',
        'tracking_id',
        'ip_address',
        'date'
    )
    list_display_links = [
        'user'
    ]
    list_filter = ['user', 'tracking_id']

    search_fields = [
        'user__username',
        'tracking_id'
    ]


admin.site.register(ProductView, TrackingAdmin)
