from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.shortcuts import reverse
from django_countries.fields import CountryField
from categories.models import Category

CATEGORY_CHOICES = (
    ('At', 'Arts, Crafts'),
    ('Bk', 'Books'),
    ('Bb', 'Baby Care'),
    ('Be', 'Beautiful2'),
    ('Ca', 'Camera & Photo'),
    ('S', 'Shirt'),
    ('Sw', 'Sport wear'),
    ('Ow', 'Outwear'),
    ('At', 'Arts, Crafts'),
    ('Am', 'Automotive & Motorcycle'),
    ('Ca', 'Cell Phones & Accessories'),
    ('El', 'Electronics'),
    ('Fa', 'Fashion'),
    ('Fu', 'Furniture'),
    ('So', 'Sokoni'),

)
LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')

)
ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping')

)


# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#
#     #     stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
#     #     one_click_purchasing = models.BooleanField()
#     #
#     def __str__(self):
#         return self.user.username


#
#
# # post save signal to create the above user
#
# def userprofile_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         userprofile = UserProfile.objects.create(user=instance)
#
#
# #
# post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)


class Product(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,
                            max_length=50,
                            help_text='Unique value for product page URL, created from name.')
    brand = models.CharField(max_length=50, blank=True, null=True)
    stock = models.BooleanField(default=True, blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    old_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, default=0.00)
    image_url = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='images/products/main')
    is_active = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    description = models.TextField()
    meta_keywords = models.CharField("Meta Keywords",
                                     max_length=255,
                                     help_text='Comma-delimited set of SEO keywords for meta tag')
    meta_description = models.CharField("Meta Description",
                                        max_length=255,
                                        help_text='Content for description meta tag')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    category_choice = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    product_categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Products'
        ordering = ['-created_at']
        verbose_name_plural = 'Products'

    def sale_price(self):
        if self.old_price > self.price:
            return self.price
        else:
            return None

    def get_absolute_url(self):
        return reverse('me2ushop:product', kwargs={'slug': self.slug})

    def get_add_cart_url(self):
        return reverse('me2ushop:add_cart', kwargs={'slug': self.slug})

        # def get_add_cart_url_product(self):
        #     return reverse('me2ushop:add_cart_product', kwargs={'slug': self.slug})

    def add_cart_qty(self):
        return reverse('me2ushop:add_cart_qty', kwargs={'slug': self.slug})

    def get_remove_cart_url(self):
        return reverse('me2ushop:remove_cart', kwargs={'slug': self.slug})

        # def get_remove_cart_url_product(self):
        #     return reverse('me2ushop:remove_single_item_cart_product', kwargs={'slug': self.slug})

    def get_order_summary_url(self):
        return reverse('me2ushop:order_summary')


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.old_price

    def get_total_saved(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_price(self):
        # if self.item.discount_price:
        #     return self.get_total_discount_price()
        # else:
        return self.get_total_price()


class CartItem(models.Model):
    cart_id = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    product = models.ForeignKey('me2ushop.Product', unique=False, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart_items'
        ordering = ['-date_added']

    def total(self):
        return self.quantity * self.product.price

    def name(self):
        return self.product.title

    def price(self):

        return self.product.price

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def augument_quantity(self, quantity):
        self.quantity += int(quantity)
        self.save()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL,
                                        blank=True, null=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL,
                                         blank=True, null=True)
    payment = models.ForeignKey('StripePayment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_coupon_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        total -= self.coupon.amount
        return total

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def total_items(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total

    def get_total_saved_coupon(self):
        return self.get_total() - self.get_coupon_total()


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=10)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    payment_option = models.CharField(max_length=10)
    default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.country)

    class Meta:
        verbose_name_plural = 'Addresses'


class StripePayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=20)
    valid = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class RequestRefund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    ref_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.pk}"
