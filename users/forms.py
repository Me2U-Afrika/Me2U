import logging

from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.core.mail import send_mail
from django.template.loader import render_to_string

from me2ushop.models import Brand
from .models import Profile, User, AutomobileProfile

logger = logging.getLogger(__name__)


class UserRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']
        field_classes = {"email": UsernameField}

    # password1 = forms.RegexField(label="Password", regex=r'^(?=.*\W+).*$',
    #                              help_text='Password must be 6 characters long and contain' \
    #                                        'at least one non-alphanumeric character.',
    #                              widget=forms.PasswordInput, min_length=6)
    # password2 = forms.RegexField(label="Password confirmation", regex=r'^(?=.*\W+).*$',
    #                              widget=forms.PasswordInput, min_length=6)
    # email = forms.EmailField(max_length='50')

    def send_mail(self):
        logger.info(
            "Sending Signup email for username=%s",
            self.cleaned_data["username"]
        )
        # message = "Welcome {}".format(self.cleaned_data["username"])
        context = {
            'username': self.cleaned_data["username"]
        }
        message = render_to_string('users/message_from_ceo.txt', context)
        email_subject = 'Welcome to Me2U|Africa. Message from CEO'
        send_mail(
            email_subject,
            message,
            'noreply@me2uafrika.com',
            [self.cleaned_data["email"]], fail_silently=True,
        )


class AutomobileRegisterForm(forms.ModelForm):
    class Meta:
        model = AutomobileProfile
        fields = '__all__'
        exclude = ['date_of_registration']


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        exclude = ['user', 'profile', 'valid_payment_method', 'active', 'is_featured', 'application_status']


class AddressForm(forms.ModelForm):
    pass
    # class Meta:
    #     model = Profile
    #     exclude = ['user', 'image', 'email', 'phone']


class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfilePicForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'image_url', 'image']
