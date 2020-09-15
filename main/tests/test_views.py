from django.test import TestCase, Client
from django.urls import reverse

from users.models import User

from me2ushop.models import Address


class TestPage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_works(self):
        response = self.client.get(reverse("me2ushop:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home-page.html')
        self.assertContains(response, 'Me2U|Africa')

    def test_about_us_page_works(self):
        response = self.client.get(reverse("main:aboutus"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')
        self.assertContains(response, 'Daniel')

    def test_address_list_page_returns_only_owned(self):
        user1 = User.objects.create_user("dm@gmail.com", "Qeautiful2222")

        user2 = User.objects.create_user("da0@gmail.com", "QWEbeautiful2")
        Address.objects.create(user=user1, apartment_address="flat 2",
                               street_address="12 Stralz avenue", address_type="B", city="Kigali", country="RW", )
        Address.objects.create(user=user2, apartment_address="flat 3",
                               street_address="Kigali heights", address_type="S", city="kicukiro", country="RW", )
        self.client.force_login(user2)
        response = self.client.get(reverse("users:address_list"))
        self.assertEqual(response.status_code, 200)
        address_list = Address.objects.filter(user=user2)
        self.assertEqual(list(response.context["object_list"]), list(address_list), )

    def test_address_create_stores_user(self):
        user1 = User.objects.create_user("dm@gmail.com", "Qeautiful2222")

        post_data = {"street_address": "1 av st",
                     "apartment_address": "Kigali",
                     "zip": "00100",
                     "address_type":"B",
                     "city": "Manchester",
                     "country": "KE",

                     }
        self.client.force_login(user1)
        self.client.post(reverse("users:address_create"), post_data)
        self.assertTrue(Address.objects.filter(user=user1).exists())

