from django.test import TestCase, Client
from django.urls import reverse


class TestPage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_works(self):
        response = self.client.get(reverse("me2ushop:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home-page.html')
        self.assertContains(response, 'Me2U|Africa')

    # def test_about_us_page_works(self):
    #     response = self.client.get(reverse("main:aboutus"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'about_us.html')
    #     self.assertContains(response, 'Daniel')
