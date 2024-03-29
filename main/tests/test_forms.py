from django.test import TestCase
from django.core import mail
from django.urls import reverse
from main import forms


class TestForm(TestCase):
    # CONTACT US FORM
    def test_valid_contact_us_form_sends_email(self):
        form = forms.ContactForm({
            'name': "Luke Skywalker",
            'email': "danielmakori0@gmail.com",
            'phone': 250785011413,
            'message': "Hi there"})
        self.assertTrue(form.is_valid())

        with self.assertLogs('main.forms', level='INFO') as cm:
            form.send_mail()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Me2UAfrika Site Message')
        self.assertGreaterEqual(len(cm.output), 1)

    def test_invalid_contact_us_form(self):
        form = forms.ContactForm({
            'message': "Hi there"})
        self.assertFalse(form.is_valid())
        
    def test_contact_us_page_works(self):
        response = self.client.get(reverse("main:contact_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_form.html')
        # self.assertContains(response, '')
        self.assertIsInstance(response.context["form"], forms.ContactForm)
