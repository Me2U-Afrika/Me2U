from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django_countries.fields import CountryField


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class SellerRegisterForm(UserRegisterForm):
    # email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        exclude = ('username',)


# class AutomobileRegisterForm(UserCreationForm):
#     phone_number = forms.CharField(max_length=20)
#     refferal_name = forms.CharField(max_length=10)
#
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email,' 'password1', 'password2']

#
# class SellerRegisterForm(UserCreationForm):
#     shop_tax_country = CountryField(multiple=False)
#     phone_number = forms.CharField(max_length=20)
#     refferal_name = forms.CharField(max_length=10)
#
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email,' 'password1', 'password2']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'image', 'email', 'phone']


class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class ProfilePicForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'image']
