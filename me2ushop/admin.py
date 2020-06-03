from django.contrib import admin
# from .models import Item, OrderItem, Order, Address, StripePayment, Coupon, RequestRefund
from .models import *


class BillingAddress(admin.ModelAdmin):
    list_display = ('user', 'street_address', 'apartment_address', 'country', 'zip', 'payment_option')


class Payment(admin.ModelAdmin):
    list_display = ('user', 'stripe_charge_id', 'amount', 'timestamp')


def make_refund_accepted(modelAdmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class Ordered(admin.ModelAdmin):
    list_display = (
        'user', 'start_date', 'order_date', 'ordered', 'payment', 'coupon', 'ref_code', 'billing_address',
        'being_delivered',
        'received', 'refund_requested', 'refund_granted')
    list_display_links = ['user', 'payment', 'coupon', 'billing_address']
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']

    search_fields = [
        'user__username',

    ]

    actions = [make_refund_accepted]


class Items_Ordered(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'ordered')


class CouponDisplay(admin.ModelAdmin):
    list_display = ('code', 'valid')
    list_filter = ['valid']


class RefundDisplay(admin.ModelAdmin):
    list_display = ('order', 'reason', 'accepted', 'ref_code')
    list_filter = ['accepted']
    list_display_links = ['order', 'ref_code']


admin.site.register(Item)
admin.site.register(OrderItem, Items_Ordered)
admin.site.register(Order, Ordered)
admin.site.register(Address, BillingAddress)
admin.site.register(StripePayment, Payment)
admin.site.register(Coupon, CouponDisplay)
admin.site.register(RequestRefund, RefundDisplay)
