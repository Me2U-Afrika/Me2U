from django.conf import settings
from Me2U.settings import PRODUCTS_PER_ROW
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.shortcuts import reverse
from django_countries.fields import CountryField
from categories.models import Category
from users.models import Profile

from PIL import Image
from django.db import models
from stdimage import StdImageField, JPEGField
import collections
from tagging.registry import register

CATEGORY_CHOICES = (
    ('At', 'Arts, Crafts'),
    ('Bk', 'Books'),
    ('Bb', 'Baby Care'),
    ('Be', 'Beautiful 2'),
    ('Ca', 'Camera & Photo'),
    ('S', 'Shirt'),
    ('Sw', 'Sport wear'),
    ('Ow', 'Outwear'),
    ('Am', 'Automotive & Motorcycle'),
    ('Ca', 'Cell Phones & Accessories'),
    ('El', 'Electronics'),
    ('Fa', 'Fashion'),
    ('Fu', 'Furniture'),
    ('So', 'Sokoni'),
    ('Wo', 'Women Fashion')
)
LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),


)
ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping')
)


class FeaturedProductManager(models.Manager):
    def all(self):
        return super(FeaturedProductManager, self).all().filter(is_active=True).filter(is_featured=True)


class BestsellerProductManager(models.Manager):
    def all(self):
        return super(BestsellerProductManager, self).all().filter(is_active=True).filter(is_bestseller=True)


class ActiveProductManager(models.Manager):
    def get_query_set(self):
        return super(ActiveProductManager, self).get_query_set().filter(is_active=True).filter(in_stock=True)


class Product(models.Model):
    title = models.CharField(max_length=100)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True,
                            max_length=50,
                            help_text='Unique value for product page URL, created from name.')
    brand = models.CharField(max_length=50, blank=True, null=True)
    stock = models.IntegerField(default=0)
    in_stock = models.BooleanField(default=True, blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    old_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, default=0.00)
    image_url = models.CharField(max_length=200, blank=True, null=True)
    # image = models.ImageField(upload_to='images/products/main')

    # creates a thumbnail resized to maximum size to fit a 100x75 area
    image = StdImageField(upload_to='images/products', blank=True, null=True, variations={
        'thumbnail': (200, 200),
        'medium': (340, 300),

    }, delete_orphans=True)

    made_in_africa = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    description = models.TextField()
    additional_information = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField("Meta Keywords",
                                     max_length=255,
                                     help_text='Comma-delimited set of SEO keywords for meta tag')
    meta_description = models.CharField("Meta Description",
                                        max_length=255,
                                        help_text='help sellers get your product easily. Give a simple short '
                                                  'description '
                                                  'about the product')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    category_choice = models.CharField(choices=CATEGORY_CHOICES, max_length=2,
                                       help_text='Choose the main category for the product'
                                       )
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, blank=True, null=True, help_text='tags the product '
                                                                                                   'primary blue, '
                                                                                                   'danger red, '
                                                                                                   'secondary purple')
    product_categories = models.ManyToManyField(Category, help_text='input the category above and any other where the '
                                                                    'product can be found in.')

    objects = models.Manager()
    active = ActiveProductManager()
    featured = FeaturedProductManager()
    bestseller = BestsellerProductManager()

    # made_in_africa = ActiveAfricaProductManager()

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

    def add_cart_qty(self):
        return reverse('me2ushop:add_cart_qty', kwargs={'slug': self.slug})

    def get_remove_cart_url(self):
        return reverse('me2ushop:remove_cart', kwargs={'slug': self.slug})

        # def get_remove_cart_url_product(self):
        #     return reverse('me2ushop:remove_single_item_cart_product', kwargs={'slug': self.slug})

    def get_order_summary_url(self):
        return reverse('me2ushop:order_summary')

    def cross_sells(self):
        orders = Order.objects.filter(items__item=self)
        order_items = OrderItem.objects.filter(order__in=orders).exclude(item=self)
        products = Product.active.filter(orderitem__in=order_items).filter().distinct()
        return products

    # def save_image(self, *args, **kwargs):
    #     product = Product.objects.get(title=self)
    #     product.image.open()
    #     imag = Image.open(product.image)
    #     if imag.width > 340 or imag.height > 300:
    #         output_size = (340, 300)
    #         imag.thumbnail(output_size)
    #         imag.save()

    def cross_sells_user(self):
        from django.contrib.auth.models import User
        users = User.objects.filter(order__items__item=self)
        items = OrderItem.objects.filter(order__user__in=users).exclude(item=self)
        products = Product.active.filter(orderitem__in=items).distinct()
        return products

    def cross_sells_hybrid(self):
        from django.contrib.auth.models import User
        from django.db.models import Q
        orders = Order.objects.filter(items__item=self)
        users = User.objects.filter(order__items__item=self)
        items = OrderItem.objects.filter(Q(order__user__in=users) |
                                         Q(order__in=orders)
                                         ).exclude(item=self)

        products = Product.active.filter(orderitem__in=items)

        matching = []

        for product in products:
            matching.append(product)

        most_products = []

        c = collections.Counter(matching)

        for product, count in c.most_common(3):
            # print('%s: %7d' % (product, count))
            most_products.append(product)
        # print('most_products:', most_products)

        return most_products


# Product model class definition here
register(Product)


class OrderItem(models.Model):
    from stats.models import ProductView
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    cart_id = models.ForeignKey(ProductView, max_length=70, blank=True, null=True, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.CASCADE, unique=False)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_absolute_url(self):
        return reverse('users:order-details', kwargs={'order_id': self.id})

    def get_total_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.old_price

    def get_total_saved(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_price(self):
        # if self.item.discount_price:
        #     return self.get_total_discount_price()
        # else:ord
        return self.get_total_price()


class OrderInfo(models.Model):
    class Meta:
        abstract = True

    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField('OrderItem')
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    payment = models.ForeignKey('StripePayment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)


class OrderAnonymous(OrderInfo):
    from stats.models import ProductView
    cart_id = models.ForeignKey(ProductView, max_length=70, blank=True, null=True, on_delete=models.CASCADE)
    billing_address = models.ForeignKey('Address', related_name='billing_address_anonymous', on_delete=models.SET_NULL,
                                        blank=True, null=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address_anonymous',
                                         on_delete=models.SET_NULL,
                                         blank=True, null=True)

    class Meta:
        ordering = ['-order_date']
        verbose_name_plural = 'OrderAnonymous'

    def __str__(self):
        return str(self.cart_id)

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


class Order(OrderInfo):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL,
                                        blank=True, null=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL,
                                         blank=True, null=True)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):

        return reverse('users:order-details', kwargs={'order_id': self.id})

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


class ActiveProductReviewManager(models.Manager):
    def all(self):
        return super(ActiveProductReviewManager, self) \
            .all().filter(is_approved=True)


class ProductReview(models.Model):
    RATINGS = ((5, 5), (4, 4), (3, 3), (2, 2), (1, 1))
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # ordered_by_user = models.ForeignKey(Order, ordered=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField(default=5, choices=RATINGS)
    is_approved = models.BooleanField(default=True)
    content = models.TextField()
    country = CountryField(multiple=False, blank=True, null=True)

    objects = models.Manager()
    approved = ActiveProductReviewManager()

    def __str__(self):
        return self.content


class Address(models.Model):
    from stats.models import ProductView
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    cart_id = models.ForeignKey(ProductView, max_length=70, blank=True, null=True, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=10)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    payment_option = models.CharField(max_length=10)
    default = models.BooleanField(default=False)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # contact info

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
        return self.stripe_charge_id


class Coupon(models.Model):
    code = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=20)
    valid = models.BooleanField(default=True)

    def __str__(self):
        return str(self.code)


class RequestRefund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    ref_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.pk}"
