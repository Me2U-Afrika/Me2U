from django.contrib import admin
from payments.models import LNMOnline, DRCTransactionModel


class LNMOnlineAdmin(admin.ModelAdmin):
    list_display = ("PhoneNumber", 'Amount', 'MpesaReceiptNumber', 'CheckoutRequestID', 'TransactionDate')


class FlutterAdmin(admin.ModelAdmin):
    list_display = ("user", 'amount', 'reference')


admin.site.register(LNMOnline, LNMOnlineAdmin)
admin.site.register(DRCTransactionModel, FlutterAdmin)
