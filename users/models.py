from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django_countries.fields import CountryField
from stdimage import StdImageField
from utils.models import CreationModificationDateMixin
from currencies.models import Currency

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


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError('Users must have a username')
        email = self.normalize_email(email)
        # email = validateEmail(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password, **extra_fields):
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
        return str(self.email, )

    def get_absolute_url(self):
        return "/users/%i/" % self.pk

    def get_email(self):
        return self.email

    @property
    def is_employee(self):
        return self.is_active and (
                self.is_superuser
                # or self.is_staff
                or self.groups.filter(name='Employees').exists()
        )

    @property
    def is_dispatcher(self):
        return self.is_active and (
                self.is_staff
                or self.groups.filter(name='Dispatchers').exists()
        )

    @property
    def is_seller(self):
        return self.is_active and self.groups.filter(name='Sellers').exists()


class EmailConfirmed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activationKey = models.CharField(max_length=200)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.email)

    def activate_user_email(self):
        activation_url = "%s%s" % (settings.SITE_URL, reverse('users:activation_view', args=[self.activationKey]))
        context = {
            "activationKey": self.activationKey,
            "activation_url": activation_url,
            "user": self.user.username
        }
        message = render_to_string('users/activation_message.txt', context)
        subject = settings.EMAIL_SUBJECT_PREFIX + "Activate Your Email"
        self.email_user(subject, message, settings.EMAIL_HOST_USER)
        # print(message)

    def email_user(self, subject, message, from_email=None, *kwargs):
        send_mail(subject, message, from_email, [self.user.email], kwargs)

    def send_mail(self):
        context = {

            "user": self.user.username
        }

        message = render_to_string('users/message_from_ceo.txt', context)
        email_subject = settings.EMAIL_SUBJECT_PREFIX + 'Welcome to Me2U|AfriKa. Message from CEO'
        send_mail(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.user.email], fail_silently=True,
        )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = StdImageField(upload_to='images/profile_pics', blank=True, null=True, default='default.svg', variations={
        'thumbnail': (150, 150),
        'medium': (200, 200),
    }, delete_orphans=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=15, null=True, blank=True,
                                  help_text="Provide official First name on passport or ID")
    middle_name = models.CharField(max_length=15, blank=True, null=True, help_text="Provide official Middle name on "
                                                                                   "passport or ID")
    last_name = models.CharField(max_length=15, null=True, blank=True,
                                 help_text="Provide official Last name on passport or ID")

    verification_id = StdImageField(upload_to='images/sellerID', blank=True, null=True, help_text='Upload your '
                                                                                                  'ID/Passport')

    active = models.BooleanField(default=True, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} profile'


BUSINESS_TYPE_CHOICE = (
    ('Co', 'Company'),
    ('Sol', 'Sole Proprietorship')
)

SUBSCRIPTION_TYPE_CHOICE = (
    ('Fr', 'Free'),
    ('Bs', 'Basic'),
    ('Pr', 'Premium')
)

UNDER_REVIEW = 10
ACTIVE = 20
VERIFIED = 30
DENIED = 40
BLOCKED = 50
STATUSES = ((UNDER_REVIEW, "Under Review"),
            (ACTIVE, "Active"),
            (VERIFIED, "Verified"),
            (DENIED, "Denied"),
            (BLOCKED, "Blocked"),
            )

SHIPPING_CAPABILITY = (
    ('Cd', 'Can Ship Abroad and Deliver Locally'),
    ('Cl', 'Can Deliver Locally'),
    ('CO', 'Not Able to Deliver')
)


AUTOMOBILE_TYPE_CHOICE = (
    ('Cr', 'Car'),
    ('Pk', 'Pick Up'),
    ('Va', 'Van'),
    ('Bs', 'Bus'),
    ('Tr', 'Truck'),
    ('Mt', 'Motor'),
    ('Bc', 'Bicycle'),
)
COUNTRIES_CHOICE = (
    ('KE', 'Kenya'),
    ('UG', 'Uganda'),
    ('TZ', 'Tanzania'),
    ('RW', 'Rwanda'),
)

VALID_CITIES_CHOICE = (
    ('Kg', 'Kigali'),
    ('Kp', 'Kampala'),
    ('Nb', 'Nairobi'),
    ('Dd', 'Dodoma'),
)


class AutomobileProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    passport_no = models.CharField(max_length=20)
    automobile_type = models.CharField(choices=AUTOMOBILE_TYPE_CHOICE, max_length=4)
    date_of_registration = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=2, choices=COUNTRIES_CHOICE)
    city_of_operation = models.CharField(max_length=2, choices=VALID_CITIES_CHOICE)
    application_status = models.IntegerField(choices=STATUSES, default=UNDER_REVIEW)


class Admin(object):
    pass
