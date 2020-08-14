from unittest.mock import patch
from django.contrib import auth
from django.test import TestCase
from django.urls import reverse

from users import forms, models


class TestPage(TestCase):
    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
        self.assertContains(response, "Me2U|Africa")

    def test_user_signup_page_submission_works(self):
        post_data = {
            "email": "user@domain.com",
            "password1": "abcabcabc",
            "password2": "abcabcabc",
        }
        with patch.object(forms.UserRegisterForm, "send_mail") as mock_send:
            response = self.client.post(reverse("users:register"), post_data)

            self.assertEqual(response.status_code, 302)
            self.assertTrue(models.User.objects.filter(email="user@domain.com").exists())
            mock_send.assert_called_once()
