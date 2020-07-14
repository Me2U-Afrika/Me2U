from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django_countries.fields import CountryField

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping')

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
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)


class Profile(BaseOrderInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def __str__(self):
        return self.user.username
