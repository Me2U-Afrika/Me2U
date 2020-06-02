from django.contrib import admin
from .models import Item, OrderItem, Order, BillingAddress, StripePayment, Coupon


class Address(admin.ModelAdmin):
    list_display = ('user', 'street_address', 'apartment_address', 'country', 'zip', 'payment_option')


class Payment(admin.ModelAdmin):
    list_display = ('user', 'stripe_charge_id', 'amount', 'timestamp')


class Ordered(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'order_date', 'ordered', 'payment', 'coupon', 'billing_address', 'being_delivered', 'received', 'refund_requested', 'refund_granted')
    list_display_links = ['user', 'payment', 'coupon', 'billing_address']
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']


class Items_Ordered(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'ordered')


class CouponDisplay(admin.ModelAdmin):
    list_display = ('code', 'valid')
    list_filter = ['valid']





admin.site.register(Item)
admin.site.register(OrderItem, Items_Ordered)
admin.site.register(Order, Ordered)
admin.site.register(BillingAddress, Address)
admin.site.register(StripePayment, Payment)
admin.site.register(Coupon, CouponDisplay)

