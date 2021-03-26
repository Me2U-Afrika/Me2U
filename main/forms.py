from django.core.mail import send_mail
from django import forms
import logging
from .models import ContactUs

logger = logging.getLogger(__name__)


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = '__all__'

    def send_mail(self):
        logger.info('Send Email To Customer Service')
        message = "From {0}\n{1}".format(
            self.cleaned_data['name'],
            self.cleaned_data['message']
        )

        send_mail(
            "Site Message",
            message,
            self.cleaned_data['email'],
            ["danielmakori0@gmail.com"],
            fail_silently=False,
        )
