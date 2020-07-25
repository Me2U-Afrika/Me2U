from django.db import models
from django.contrib.auth.models import User
from me2ushop.models import Product
from django.views.generic import ListView, DetailView, View


class PageView(models.Model):
    class Meta:
        abstract = True
    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    tracking_id = models.CharField(max_length=70)
    valid_tracker = models.BooleanField(default=True)


class ProductView(PageView):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.tracking_id
