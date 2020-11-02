from django import forms
from .models import MarketingEmails


class EmailForm(forms.Form):
    email = forms.EmailField(max_length=200)
