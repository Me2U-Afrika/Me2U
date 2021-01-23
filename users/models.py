import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django_countries.fields import CountryField
from stdimage import StdImageField
from utils.models import CreationModificationDateMixin

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


#
# def validateEmail(email):
#     print('we came to validate email:', email)
#     from django.core.validators import validate_email
#     from django.core.exceptions import ValidationError
#     try:
#         validate_email(email)
#         return True
#     except ValidationError:
#         raise ValueError("Users must a valid email address")


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
        return self.is_active and (
                self.is_staff
                or self.groups.filter(name='Sellers').exists()
        )


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

        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        #
        # message = Mail(
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     to_emails=self.user.email,
        #     subject=subject,
        #     html_content=message)
        # try:
        #     sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        #     response = sg.send(message)
        #     print(response.status_code)
        #     print(response.body)
        #     print(response.headers)
        # except Exception as e:
        #     print(e)

        # return requests.post(
        #     settings.MAILGUN_ACCESS_KEY,
        #     auth=("api", settings.MAILGUN_API_KEY),
        #     data={"from": settings.EMAIL_HOST,
        #           "to": [self.user.email],
        #           "subject": subject,
        #           "text": message})

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

    #     # from sendgrid.helpers.mail import Mail
    #
    #     from sendgrid import SendGridAPIClient
    #     from sendgrid.helpers.mail import Mail
    #
    #     message = Mail(
    #         from_email=settings.DEFAULT_FROM_EMAIL,
    #         to_emails=self.user.email,
    #         subject=email_subject,
    #         html_content=message)
    #     try:
    #         sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    #         response = sg.send(message)
    #         print(response.status_code)
    #         print(response.body)
    #         print(response.headers)
    #     except Exception as e:
    #         print(e)

    # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    # data = {
    #     "personalizations": [
    #         {
    #             "to": [
    #                 {
    #                     "email": self.user.email
    #                 }
    #             ],
    #             "subject": email_subject
    #         }
    #     ],
    #     "from": {
    #         "email": settings.DEFAULT_FROM_EMAIL,
    #     },
    #     "content": [
    #         {
    #             "type": "text/plain",
    #             "value": message
    #         }
    #     ]
    # }
    # response = sg.client.mail.send.post(request_body=data)
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)


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
        'thumbnail': (200, 200),
    }, delete_orphans=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.user.email} profile'


BUSINESS_TYPE_CHOICE = (
    ('Co', 'Company'),
    ('Sol', 'Sole Proprietorship')
)

SUBSCRIPTION_TYPE_CHOICE = (
    ('Bs', 'Basic'),
    ('Pr', 'Premium')
)

UNDER_REVIEW = 10
ACTIVE = 20
DENIED = 30
BLOCKED = 40
STATUSES = ((UNDER_REVIEW, "Under Review"),
            (ACTIVE, "Active"),
            (DENIED, "Denied"),
            (BLOCKED, "Blocked"),
            )


class BusinessInformation(models.Model):
    pass


class SellerProfile(CreationModificationDateMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    business_description = models.TextField()
    email = models.EmailField(max_length=254, unique=True, help_text='Provide Business email '
                                                                     'where customers can send'
                                                                     ' inquries')
    phone = models.CharField(max_length=20, help_text='This number will be visible to buyers '
                                                      'who would like to contact you for '
                                                      'services. i.e +250785011413')
    website_link = models.CharField(max_length=30, blank=True, null=True, help_text='If you have a website by which '
                                                                                    'buyers can find out more about '
                                                                                    'your services.e.g. '
                                                                                    'https://www.facebook.com')
    facebook = models.CharField(max_length=255, blank=True, null=True, help_text='Do you have a facebook page. '
                                                                                 'Copy '
                                                                                 'paste your page link here '
                                                                                 'e.g.. '
                                                                                 'https://www.facebook.com'
                                                                                 '/Me2UAfrika')
    instagram = models.CharField(max_length=255, blank=True, null=True, help_text='Do you have a instagram page. Copy '
                                                                                  'paste your page link here eg. '
                                                                                  'https://www.instagram.com'
                                                                                  '/me2u_afrika/')
    telegram = models.CharField(max_length=100, blank=True, null=True, help_text='Do you have a Telegram Channel. Copy '
                                                                                 'paste your page link here. e.g.. '
                                                                                 'https://t.me/me2uafrika')
    business_type = models.CharField(choices=BUSINESS_TYPE_CHOICE, max_length=4)
    date_of_registration = models.DateField
    country = CountryField(multiple=False)
    subscription_type = models.CharField(max_length=2, choices=SUBSCRIPTION_TYPE_CHOICE,
                                         help_text='Select a monthly recurring subscription fees')
    application_status = models.IntegerField(choices=STATUSES, default=UNDER_REVIEW)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user.username)


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
