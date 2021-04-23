from django.contrib import admin
from payments.models import LNMOnline


class LNMOnlineAdmin(admin.ModelAdmin):
    list_display = ("PhoneNumber", 'Amount', 'MpesaReceiptNumber', 'CheckoutRequestID', 'TransactionDate')


admin.site.register(LNMOnline, LNMOnlineAdmin)
