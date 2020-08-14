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


class FrontendTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.maximize_window()
        cls.selenium.implicitly_wait(20)
        # cls.selenium.find_element_by_class_name('current-image').send_keys('test')
        # cls.selenium.quit()
        # try:
        #     cls.selenium.implicitly_wait(10).until(
        #         element=EC.presence_of_element_located((By.ID, ".current-image"))
        #     )
        # finally:
        #     cls.selenium.quit()

        # current_image = None
        # while current_image == None:
        #     current_image = WebDriverWait(cls.selenium, 10).until(
        #         EC.presence_of_element_located((By.CLASS_NAME, ".current-image"))
        #     )
        # current_image.send_keys('test')

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_product_page_switches_images_correctly(self):
        # product = models.Product.objects.get(slug='farm-vegetables')
        # print('product', product)
        # user = User.objects.get(email='danielmakori0@gmail.com')

        product = models.Product.objects.create(title="Farm Vegetables",
                                                slug="farm-vegetables",
                                                brand="Gloceries & Vegetables",
                                                price="20.00", )

        for fname in ['media/images/localProduce/Local6.jpg', 'media/images/localProduce/Local7.jpg',
                      'media/images/localProduce/Local8.jpg']:
            with open(fname, "rb", buffering=0) as f:
                image = models.ProductImage(item=product,
                                            image=ImageFile(f, name=fname), )
                image.save()

        self.selenium.get(
            "%s%s"
            % (
                self.live_server_url, reverse('me2ushop:product', kwargs={'slug': 'farm-vegetables'}, ),
            )
        )

        current_image = self.selenium.find_element_by_css_selector(
            ".current-image > img:nth-child(1)").get_attribute("src")
        self.selenium.find_element_by_css_selector("div.img:nth-child(3) > img:child(1)").click()
        new_image = self.selenium.find_element_by_css_selector(
            ".current-image > img:nth-child(1)").get_attribute("src")
        self.assertNotEqual(current_image, new_image)
