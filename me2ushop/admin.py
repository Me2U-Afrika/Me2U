from django.contrib import admin
# from .models import Item, OrderItem, Order, Address, StripePayment, Coupon, RequestRefund
from .models import *


class Payment(admin.ModelAdmin):
    list_display = ('user', 'stripe_charge_id', 'amount', 'timestamp')


def make_refund_accepted(modelAdmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


def make_coupon_accepted(modelAdmin, request, queryset):
    queryset.update(valid=True)


make_coupon_accepted.short_description = 'Update coupon to valid'


class Ordered(admin.ModelAdmin):
    list_display = (
        'user',
        'start_date',
        'order_date',
        'ordered',
        'payment',
        'coupon',
        'ref_code',
        'billing_address',
        'shipping_address',
        'being_delivered',
        'received', 'refund_requested', 'refund_granted')
    list_display_links = [
        'user',
        'shipping_address',
        'payment',
        'coupon',
        'billing_address']
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']

    search_fields = [
        'user__username',
        'ref_code'

    ]

    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]

    list_filter = ['country', 'default', 'address_type', 'country']
    search_fields = [
        'user',
        'street_address',
        'apartment_address',
        'zip'
    ]


class Items_Ordered(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'ordered')


class CouponDisplay(admin.ModelAdmin):
    list_display = ('code', 'valid')
    list_filter = ['valid']
    actions = [make_coupon_accepted]


class RefundDisplay(admin.ModelAdmin):
    list_display = ('order', 'reason', 'accepted', 'ref_code')
    list_filter = ['accepted']
    list_display_links = ['order', 'ref_code']


class ProductAdmin(admin.ModelAdmin):
    # form = ProductAdminForm()
    list_display = ('title', 'price', 'old_price', 'made_in_africa', 'created_at', 'updated_at',)
    list_display_links = ('title',)
    list_per_page = 50
    ordering = ['-created_at']

    search_fields = ['title', 'description', 'meta_keywords', 'meta_description', 'made_in_africa']
    exclude = ('created_at', 'updated_at',)

    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Product, ProductAdmin)
admin.site.register(OrderItem, Items_Ordered)
admin.site.register(Order, Ordered)
admin.site.register(StripePayment, Payment)
admin.site.register(Coupon, CouponDisplay)
admin.site.register(RequestRefund, RefundDisplay)
admin.site.register(Address, AddressAdmin)
