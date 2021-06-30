from django.db import models

# Create your models here.
from Me2U import settings
from me2ushop.models import Order
from utils.models import CreationModificationDateMixin


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


class DRCTransactionModel(CreationModificationDateMixin):
    """Represents a transaction for a specific payment type and user"""

    order = models.ForeignKey(
        to=Order, related_name="order", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="drc_transactions",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    reference = models.CharField(max_length=200)
    flutterwave_reference = models.CharField(max_length=200)
    order_reference = models.CharField(max_length=200)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    charged_amount = models.DecimalField(decimal_places=2, max_digits=9)
    status = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Flutterwave Transaction"
        verbose_name_plural = "Flutterwave Transactions"

    def __str__(self):
        return self.reference
