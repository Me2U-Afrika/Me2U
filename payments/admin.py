from django.contrib import admin
from payments.models import LNMOnline


class LNMOnlineAdmin(admin.ModelAdmin):
    list_display = ('CheckoutRequestID', 'Amount', "PhoneNumber", 'MpesaReceiptNumber', 'TransactionDate')


admin.site.register(LNMOnline, LNMOnlineAdmin)
