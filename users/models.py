from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from django_countries.fields import CountryField
from django_resized import ResizedImageField
from stdimage import StdImageField

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
    ('T', 'Both'),

)

PAYMENT_OPTIONS = (
    ('M', "M-Pesa"),
    ('P', "Paypal"),
    ('S', "Stripe"),
    ('D', "Debit Card"),
    ('C', "Cash On Delivery"),
)


# Create your models here.

class BaseOrderInfo(models.Model):
    class Meta:
        abstract = True

    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=10)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    payment_option = models.CharField(max_length=10)
    default = models.BooleanField(default=False)
    email = models.EmailField(max_length=50, blank=True, null=True, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)


class Profile(BaseOrderInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = StdImageField(upload_to='images/profile_pics', blank=True, null=True, default='default.svg', variations={
        'thumbnail': (300, 300),
    }, delete_orphans=True)

    def __str__(self):
        return f'{self.user.username} profile'


class BusinessInformation(models.Model):
    pass


class Seller_Profile(BaseOrderInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = StdImageField(upload_to='images/profile_pics/sellers', blank=True, null=True, default='default.svg', variations={
        'thumbnail': (300, 300)}, delete_orphans=True)

