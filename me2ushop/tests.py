from django.shortcuts import redirect
from django.test import TestCase, Client
from django.contrib.auth import SESSION_KEY
from django.urls import reverse
from categories.models import Category

# import httplib


class NewUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_view_category(self):
        category = Category.objects.all()[0]
        category_url = category.get_absolute_url()
        # test loading of category page
        response = self.client.get(category_url)
        # test that we got a response

        # test that the HTTP status code was "OK"
        self.assertEqual(response.status_code, 200)
