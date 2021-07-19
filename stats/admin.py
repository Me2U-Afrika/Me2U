from django.contrib import admin
from .models import PageView, ProductView, BrandView


# Register your models here.

class TrackingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'product',
        'tracking_id',
        'valid_tracker',
        'ip_address',
        'date'
    )
    list_display_links = [
        'user'
    ]
    list_filter = ['user', 'valid_tracker']

    search_fields = [
        'user__username',
        'tracking_id'
    ]


class ContactTrackingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'brand',
        'tracking_id',
        'valid_tracker',
        'ip_address',
        'date'
    )
    list_display_links = [
        'user'
    ]
    list_filter = ['user', 'valid_tracker']

    search_fields = [
        'user__username',
        'tracking_id'
    ]


admin.site.register(ProductView, TrackingAdmin)
admin.site.register(BrandView, ContactTrackingAdmin)
