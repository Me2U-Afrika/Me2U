from django.conf import settings
from Me2U.settings import PRODUCTS_PER_ROW
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count
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

PAYMENT_CHOICES = {

    ('M', "M-Pesa"),
    ('P', "Paypal"),
    ('S', "Stripe"),
    ('D', "Debit Card"),
    ('C', "Cash On Delivery"),

}


class ActiveProductManager(models.Manager):
    def all(self):
        return super(ActiveProductManager, self).all().filter(is_active=True).filter(productimage__in_display=True)


class FeaturedProductManager(ActiveProductManager):
    def all(self):
        return super(FeaturedProductManager, self).all().filter(is_featured=True)


class BestsellerProductManager(ActiveProductManager):
    def all(self):
        return super(BestsellerProductManager, self).all().filter(is_bestseller=True)


class ProductManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Product(models.Model):
    title = models.CharField(max_length=100)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    slug = models.SlugField(unique=True,
                            max_length=50,
                            help_text='Unique value for product page URL, created from the product title.')
    brand = models.CharField(max_length=50, help_text='Your store name')
    stock = models.IntegerField(default=0)
    in_stock = models.BooleanField(default=True, blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    discount_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, default=0.00)
    made_in_africa = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    description = models.TextField()
    additional_information = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField("Meta Keywords",
                                     max_length=100,
                                     help_text='Comma-delimited set of SEO keywords that summarize the type of '
                                               'product above max 4 words')
    meta_description = models.CharField("Meta Description",
                                        max_length=255,
                                        help_text='help sellers get your product easily. Give a simple short '
                                                  'description '
                                                  'about the page content you have added. This information makes it'
                                                  'easy for customers to get your product and offers an overview of it'
                                        )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    category_choice = models.CharField(choices=CATEGORY_CHOICES, max_length=2,
                                       help_text='Choose the main category for the product'
                                       )
    label = models.CharField(choices=LABEL_CHOICES,
                             max_length=1,
                             blank=True,
                             null=True,
                             help_text='tags the product NEW upon upload for the next 24 hours'
                                       'primary blue, '
                                       'danger red, '
                                       'secondary purple')
    product_categories = models.ManyToManyField(Category, blank=True,
                                                help_text='input the category above and any other where the '
                                                          'product can be found in.')

    objects = ProductManager()
    active = ActiveProductManager()
    featured = FeaturedProductManager()
    bestseller = BestsellerProductManager()

    # made_in_africa = ActiveAfricaProductManager()

    def __str__(self):
        return self.title

    # def clean(self):
    #     # Don't all)ow draft entries to have a pub_date.
    #     if self.seller != settings.AUTH_USER_MODEL:
    #         print(self.seller)
    #         print(settings.AUTH_PROFILE_MODULE)
    #
    #         raise ValidationError('Please select your seller email prior to adding. Make sure the selected email '
    #                               'belongs to you.')

    def natural_key(self):
        return (self.slug,)

    class Meta:
        db_table = 'Products'
        ordering = ['-created_at']
        verbose_name_plural = 'Products'

    def sale_price(self):
        if self.discount_price:
            return self.discount_price
        else:
            return self.price

    def get_absolute_url(self):

        return reverse('me2ushop:product', kwargs={'slug': self.slug})

    def get_add_cart_url(self):
        return reverse('me2ushop:add_cart', kwargs={'slug': self.slug})

    def get_remove_cart_url(self):
        return reverse('me2ushop:remove_cart', kwargs={'slug': self.slug})

    def get_order_summary_url(self):
        return reverse('me2ushop:order_summary')

    def cross_sells(self):
        orders = Order.objects.filter(items__item=self)
        order_items = OrderItem.objects.filter(order__in=orders).exclude(item=self)
        products = Product.active.filter(orderitem__in=order_items).filter().distinct()
        return products

    def cross_sells_user(self):
        from users.models import User

        users = User.objects.filter(order__items__item=self)
        items = OrderItem.objects.filter(order__user__in=users).exclude(item=self)
        products = Product.active.filter(orderitem__in=items).distinct()
        return

    def cross_sells_sellers(self):
        from search.search import _prepare_words
        from users.models import User
        from django.db.models import Q

        users = User.objects.filter(product__title__icontains=self)
        print('other sellers:', users)
        print('self', self.slug)
        words = _prepare_words(self.title)
        print('words:', words)

        for word in words:
            products = Product.active.filter(Q(title__icontains=word) |
                                             Q(title__startswith=self) |
                                             Q(title__endswith=self)
                                             ).exclude(slug=self.slug)
            print('from sellers', products)
            return products

    def cross_sells_hybrid(self):
        from users.models import User

        from django.db.models import Q
        orders = Order.objects.filter(items__item=self)
        users = User.objects.filter(order__items__item=self)
        # print('users', users)
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

    # def save_model(self):
    #     if self.stock < 1:
    #         self.is_active = False
    #     else:
    #         self.is_active = True


# Product model class definition here
# tags register
register(Product)


class DisplayImageManager(models.Manager):
    def get_query_set(self):
        return super(DisplayImageManager, self).get_query_set().filter(in_display=True)


class ProductImage(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    image = StdImageField(upload_to='images/products', blank=True, null=True, variations={
        'thumbnail': (200, 200),
        'medium': (340, 300),

    }, delete_orphans=True)
    in_display = models.BooleanField(default=True)

    objects = models.Manager()
    displayed = DisplayImageManager()

    class Meta:
        ordering = ('-in_display',)

    def get_absolute_url(self):
        return reverse('me2ushop:product_images', kwargs={'slug': self.item.slug})


class OrderItem(models.Model):
    from stats.models import ProductView
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40
    IN_TRANSIT = 45
    DELIVERED = 50
    STATUSES = ((NEW, "New"),
                (PROCESSING, "Processing"),
                (SENT, "Sent"),
                (CANCELLED, "Cancelled"),
                (IN_TRANSIT, "in_transit"),
                (DELIVERED, "Delivered"),
                )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    cart_id = models.CharField(max_length=40, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.PROTECT, unique=False, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    delivered_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='dispatcher', on_delete=models.SET_NULL,
                                     blank=True, null=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_absolute_url(self):
        return reverse('users:order-details', kwargs={'order_id': self.id})

    def get_total_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_total_saved(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        else:
            return self.get_total_price()

    @property
    def mobile_thumb_url(self):
        products = [self.item]
        # print('products:', products)
        if products:
            img = products[0].productimage_set.first()
            if img:
                return img.image.thumbnail.url

    @property
    def summary(self):
        pieces = ['%s x %s' % (self.quantity, self.item.title)]

        return ",".join(pieces)


class Order(models.Model):
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = ((NEW, 'New'), (PAID, 'Paid'), (DONE, 'Done'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, db_index=True)
    cart_id = models.CharField(max_length=40, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    items = models.ManyToManyField('OrderItem')
    ref_code = models.CharField(max_length=20)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    payment = models.ForeignKey('StripePayment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    name = models.CharField(max_length=60, blank=True, null=True)
    billing_address1 = models.CharField(max_length=60)
    billing_address2 = models.CharField(max_length=60, blank=True)
    billing_zip_code = models.CharField(max_length=12)
    billing_country = models.CharField(max_length=3)
    billing_city = models.CharField(max_length=12, blank=True, null=True)

    # shipping_name = models.CharField(max_length=60, blank=True, null=True)
    shipping_address1 = models.CharField(max_length=60)
    shipping_address2 = models.CharField(max_length=60, blank=True)
    shipping_zip_code = models.CharField(max_length=12)
    shipping_country = models.CharField(max_length=3)
    shipping_city = models.CharField(max_length=12, blank=True, null=True)

    last_spoken_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="cs_chats",
                                       on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-order_date']

    # def __str__(self):
    #     return self.user.email

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
        # total = self.orderitem_set.all().count()
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity

        return total

    def get_total_saved_coupon(self):
        return self.get_total() - self.get_coupon_total()

    @property
    def mobile_thumb_url(self):
        products = [i.item for i in self.items.all()]
        # print('products:', products)
        if products:
            img = products[0].productimage_set.first()
            if img:
                return img.image.thumbnail.url

    @property
    def summary(self):
        product_counts = self.items.values(
            'quantity', 'item__title'
        )
        pieces = []
        for pc in product_counts:
            pieces.append(
                '%s x %s' % (pc['quantity'], pc['item__title'])
            )
        return ",".join(pieces)


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
    # cart_id = models.ForeignKey(ProductView, max_length=70, blank=True, null=True, on_delete=models.CASCADE)
    cart_id = models.CharField(max_length=40, blank=True, null=True)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    city = models.CharField(max_length=60)
    zip = models.CharField(max_length=10)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    payment_option = models.CharField(max_length=2, choices=PAYMENT_CHOICES)
    default = models.BooleanField(default=False)
    name = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    # contact info

    def __str__(self):
        # return str(self.country)
        return ''.join(str(self.street_address) + ' ' + str(self.country))

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-date_updated']


class StripePayment(models.Model):
    from stats.models import ProductView
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    cart_id = models.ForeignKey(ProductView, max_length=70, blank=True, null=True, on_delete=models.CASCADE)
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
# class OrderAnonymous(OrderInfo):
#     from stats.models import ProductView
#     cart_id = models.ForeignKey(ProductView, max_length=70, blank=True, null=True, on_delete=models.CASCADE)
#     billing_address = models.ForeignKey('Address', related_name='billing_address_anonymous', on_delete=models.SET_NULL,
#                                         blank=True, null=True)
#     shipping_address = models.ForeignKey('Address', related_name='shipping_address_anonymous',
#                                          on_delete=models.SET_NULL,
#                                          blank=True, null=True)
#
#     class Meta:
#         ordering = ['-order_date']
#         verbose_name_plural = 'OrderAnonymous'
#
#     def __str__(self):
#         return str(self.cart_id)
#
#     def get_total(self):
#         total = 0
#         for order_item in self.items.all():
#             total += order_item.get_final_price()
#         return total
#
#     def total_items(self):
#         total = 0
#         for order_item in self.items.all():
#             total += order_item.quantity
#         return total
#
