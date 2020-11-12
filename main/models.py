from django.db import models
from django.utils import timezone
# from django.contrib.auth.models import User
from users.models import User
from django.core.validators import MinValueValidator

from me2ushop.models import Product


class ContactUs(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=30)
    email = models.EmailField
    message = models.TextField(max_length=600, help_text='Max length is 600 characters. Make your inquiry brief and '
                                                         'to the point')

    def __str__(self):
        return str(self.name)


AINA_YA_NDAI = (
    ('BI', 'Baiskeli'),
    ('MK', 'MotorBike'),
    ('CR', 'Car'),
    ('LO', 'Lorry')

)

WATEJA = (
    ('A', 'Passengers'),
    ('M', 'Mizigo')

)


class MaDere(models.Model):
    name = models.CharField(max_length=255)
    Namba = models.CharField(max_length=13)
    price_per_km = models.FloatField()
    location = models.CharField(max_length=255)
    availability = models.BooleanField()
    image_url = models.CharField(max_length=2083, blank=True, null=True)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image_Ndai = models.ImageField(upload_to='Ma_Ndai', blank=True, null=True)
    license_verified = models.BooleanField(default=False)
    type_of_automobile = models.CharField(choices=AINA_YA_NDAI, max_length=2)
    customers = models.CharField(choices=WATEJA, max_length=1)

    def __str__(self):
        return self.name

# Same as the Order class
# class Basket(models.Model):
#     OPEN = 10
#     SUBMITTED = 20
#     # Same as Ordered = False/True
#     STATUSES = ((OPEN, 'Open'), (SUBMITTED, 'Submitted'))
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
#     status = models.IntegerField(choices=STATUSES, default=OPEN)
#
#     def is_empty(self):
#         return self.basketline_set.all().count() == 0
#
#     # Same as total_items
#     def count(self):
#         return sum(item.quantity for item in self.basketline_set.all())
#
#
# # same as the order_item class @ me2ushop.models
# class BasketLine(models.Model):
#     basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

# class Referrals(models.Model):
#     link = models.CharField(max_length=2083)
#     description = models.CharField(max_length=255)
#     discount = models.FloatField()
#
#
# class ads(models.Model):
#     ad_type = models.CharField(max_length=60)
#     ad_description = models.TextField()
#     ad_requirements = models.CharField(max_length=255)
#     # date_posted = models.DateTimeField(default=timezone.now)
#     # Addicts = models.ForeignKey(Addicts)
#
#
# class templatetags(models.Model):
#     name = models.CharField(max_length=30)
#
#     def __str__(self):
#         return self.name
