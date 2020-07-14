from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'image', 'email', 'phone']


class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'image', 'email', 'phone']
