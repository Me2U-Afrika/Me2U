from decimal import Decimal
from telnetlib import EC
from django.urls import reverse
from django.core.files.images import ImageFile
from django.contrib.staticfiles.testing import (StaticLiveServerTestCase)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from me2ushop import models
from selenium.webdriver.support.wait import WebDriverWait
from users.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from main import factories
from django.test import tag


# @tag('e2e')
# class FrontendTests(StaticLiveServerTestCase):
#     selenium = None
#
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.selenium = WebDriver()
#         cls.selenium.maximize_window()
#         cls.selenium.implicitly_wait(20)
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super().tearDownClass()
#
#     def test_product_page_switches_images_correctly(self):
#         # product = models.Product.objects.get(slug='farm-vegetables')
#         # print('product', product)
#         # user = User.objects.get(email='danielmakori0@gmail.com')
#
#         product = models.Product.objects.create(title="Farm Vegetables",
#                                                 slug="farm-vegetables",
#                                                 brand="Gloceries & Vegetables",
#                                                 price="20.00", )
#
#         for fname in ['media/images/localProduce/Local6.jpg', 'media/images/localProduce/Local7.jpg',
#                       'media/images/localProduce/Local8.jpg']:
#             with open(fname, "rb", buffering=0) as f:
#                 image = models.ProductImage(item=product,
#                                             image=ImageFile(f, name=fname), )
#                 image.save()
#
#         self.selenium.get(
#             "%s%s"
#             % (
#                 self.live_server_url, reverse('me2ushop:product', kwargs={'slug': 'farm-vegetables'}, ),
#             )
#         )
#
#         current_image = self.selenium.find_element_by_css_selector(
#             "current-image").get_attribute("src")
#         self.selenium.find_element_by_css_selector("div.img:nth-child(3) > img:child(1)").click()
#         new_image = self.selenium.find_element_by_css_selector(
#             ".current-image > img.image:nth-child(1)").get_attribute("src")
#         self.assertNotEqual(current_image, new_image)

class TestEndpoints(APITestCase):
    def test_mobile_login_works(self):
        user = User.objects.create_user(
            username='daniel',
            email='danielmakori0@gmail.com',
            password='welcome28'
        )
        response = self.client.post(
            reverse('me2ushop:mobile_token'),
            {'username': 'danielmakori0@gmail.com', 'password': 'welcome28'},
        )
        jsonresp = response.json()
        self.assertIn('token', jsonresp)

    def test_mobile_flow(self):
        user = factories.UserFactory()
        token = Token.objects.get(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        a = factories.ProductFactory(
            title='Sausage', slug='sausage', is_active=True, price=12.00
        )
        b = factories.ProductFactory(
            title='meat', slug='meat', is_active=True, price=14.00
        )
        order_item_a = factories.OrderItemFactory.create_batch(
            1, quantity=2, item=a, user=user
        )
        print('orderitem_a:', order_item_a[0].id)

        order_item_b = factories.OrderItemFactory.create_batch(
            1, quantity=2, item=b, user=user
        )
        print('orderitem_b:', order_item_b)

        response = self.client.get(reverse('me2ushop:mobile_my_orders'))
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )

        expected = [
            {
                'id': order_item_b[0].id,
                'image': None,
                'price': 28.0,
                'summary': '2 x meat',
            },
            {
                'id': order_item_a[0].id,
                'image': None,
                'price': 24.0,
                'summary': '2 x Sausage',
            },
        ]
        self.assertEqual(response.json(), expected)
