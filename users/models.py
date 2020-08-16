from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
import django.contrib.auth.validators

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

# class BaseOrderInfo(models.Model):
#     class Meta:
#         abstract = True
#
#     street_address = models.CharField(max_length=100)
#     apartment_address = models.CharField(max_length=100)
#     country = CountryField(multiple=False)
#     zip = models.CharField(max_length=10)
#     address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
#     payment_option = models.CharField(choices=PAYMENT_OPTIONS)
#     default = models.BooleanField(default=False)
#     email = models.EmailField(max_length=50, blank=True, null=True, unique=True)
#     phone = models.CharField(max_length=20, blank=True, null=True)


class BusinessInformation(models.Model):
    pass


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError('Users must have a username')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email,username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self._create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=254, unique=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', ]

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return "/users/%i/" % self.pk

    def get_email(self):
        return self.email

    @property
    def is_employee(self):
        return self.is_active and (
                self.is_superuser
                or self.is_staff
                and self.groups.filter(name='Employees').exists()
        )

    @property
    def is_dispatcher(self):
        return self.is_active and (
                self.is_superuser
                or self.is_staff
                and self.groups.filter(name='Dispatchers').exists()
        )

    @property
    def is_seller(self):
        return self.is_active and (
                self.is_superuser
                or self.is_staff
                and self.groups.filter(name='Sellers').exists()
        )


# class user_type(models.Model):
#     is_seller = models.BooleanField(default=False)
#     is_service_provider = models.BooleanField(default=False)
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#
#     def __str__(self):
#         if self.is_seller:
#             return User.get_email(self.user) + " - is_seller"
#         elif self.is_service_provider:
#             return User.get_email(self.user) + " - is_service_provider"
#         else:
#             return User.get_email(self.user) + " - is_buyer"
#

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = StdImageField(upload_to='images/profile_pics', blank=True, null=True, default='default.svg', variations={
        'thumbnail': (300, 300),
    }, delete_orphans=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.user.email} profile'


class Seller_Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = StdImageField(upload_to='images/profile_pics/sellers', blank=True, null=True, default='default.svg',
                          variations={
                              'thumbnail': (300, 300)}, delete_orphans=True)
