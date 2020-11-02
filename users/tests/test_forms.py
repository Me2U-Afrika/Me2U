from django.core import mail
from django.test import TestCase

from users import forms


class TestForm(TestCase):
    def test_valid_signup_form_sends_email(self):
        form = forms.UserRegisterForm({
            "username": "Ogechi",
            "email": "user@domain.com",
            "password1": "abcabcabc",
            "password2": "abcabcabc",
        })

        self.assertTrue(form.is_valid())
        with self.assertLogs("users.forms", level="INFO") as cm:
            form.send_mail()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome to Me2U|Africa. Message from CEO")
        self.assertGreaterEqual(len(cm.output), 1)
