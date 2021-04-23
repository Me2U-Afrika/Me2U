from django.db import models


# Create your models here.

class LNMOnline(models.Model):
    CheckoutRequestID = models.CharField(max_length=50, editable=False)
    MerchantRequestID = models.CharField(max_length=20, editable=False)
    ResultCode = models.IntegerField(editable=False)
    ResultDesc = models.CharField(max_length=120, editable=False)
    Amount = models.FloatField(editable=False)
    MpesaReceiptNumber = models.CharField(max_length=15, editable=False)
    Balance = models.CharField(max_length=12, blank=True, null=True, editable=False)
    TransactionDate = models.DateTimeField(editable=False)
    PhoneNumber = models.CharField(max_length=13, editable=False)

    def __str__(self):
        return f"{self.PhoneNumber} has sent {self.Amount} >> {self.MpesaReceiptNumber}"
