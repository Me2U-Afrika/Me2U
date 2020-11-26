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
from categories.models import Category, Department
from users.models import Profile
from utils.models import CreationModificationDateMixin
from sellers.models import Sellers
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
        return super(ActiveProductManager, self).all().filter(is_active=True)


class FeaturedProductManager(ActiveProductManager):
    def all(self):
        return super(FeaturedProductManager, self).all().filter(is_featured=True)


class BestsellerProductManager(ActiveProductManager):
    def all(self):
        return super(BestsellerProductManager, self).all().filter(is_bestseller=True)


class ProductManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Brand(CreationModificationDateMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, unique=True, help_text='Unique title to identify Your store and your '
                                                                    'product line')
    active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, blank=True, null=True)
    image = StdImageField(upload_to='images/brands/brand_background', blank=True, null=True,
                          help_text='wallpaper for your store.Leave blank if you don\'t have one',
                          default='images/brands/brand_background/default.jpg')
    logo = StdImageField(upload_to='images/brands/brand_logo', blank=True, null=True, help_text='logo for your store, '
                                                                                                'Leave blank if you '
                                                                                                'don\'t have one', )

    def __str__(self):
        return str(self.title)


class Product(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,
                            max_length=50,
                            help_text='Unique value for product page URL, created from the product title.')
    brand_name = models.ForeignKey('Brand', on_delete=models.SET_NULL, blank=True, null=True,
                                   help_text='Your store name')
    stock = models.IntegerField(default=1)
    sku = models.CharField(max_length=120)
    in_stock = models.BooleanField(default=True, blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    discount_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(1.0)])
    made_in_africa = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_bestrated = models.BooleanField(default=False)

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

    product_categories = models.ManyToManyField(Department,

                                                help_text='input the subcategory.')

    objects = ProductManager()
    active = ActiveProductManager()
    featured = FeaturedProductManager()
    bestseller = BestsellerProductManager()

    # made_in_africa = ActiveAfricaProductManager()

    def __str__(self):
        return str(self.title)

    # def clean(self):
    #     # Don't allow draft entries to have a pub_date.
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

    def total_items_ordered(self):
        orders = self.orderitem_set.all()
        total = 0
        for order_item in orders:
            if order_item.ordered:
                total += order_item.quantity

        return total

    def total_discount(self):
        # orders = self.orderitem_set.all()
        diff = ((self.price - self.discount_price) / self.price) * 100
        return round(diff)

    def get_absolute_url(self):

        return reverse('me2ushop:product', kwargs={'slug': self.slug})

    def get_add_cart_url(self):
        return reverse('me2ushop:add_cart', kwargs={'slug': self.slug})

    def get_images(self):
        return self.productimage_set.all()

    def get_image_in_display(self):
        image = self.productimage_set.filter(in_display=True)
        if image:
            return image[0]

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

        category = self.category_choice
        name = self.title
        # print('category:', category)
        print('name:', name)
        # print('other sellers:', users)
        # print('self', self.slug)
        words = _prepare_words(self.title)
        print('words:', words)

        for word in words:
            products = Product.active.filter(
                Q(title__icontains=self) |
                Q(title__startswith=self) |
                Q(title__icontains=word) |
                Q(title__startswith=word) |
                Q(title__endswith=self) |
                Q(title__endswith=word)
            ).filter(category_choice=self.category_choice).exclude(slug=self.slug)
            # print('from sellers', products)
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


class ProductImage(CreationModificationDateMixin):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = StdImageField(upload_to='images/products', variations={
        'thumbnail': (170, 115, True),
        'medium': (365, 365),
        'deals_size': (365, 365, True),
        'large': (415, 470, True),

    }, delete_orphans=True)
    in_display = models.BooleanField(default=True)

    objects = ProductManager()
    displayed = DisplayImageManager()

    class Meta:
        ordering = ('-created',)

    def natural_key(self):
        return (self.slug,)

    def __str__(self):
        return str(self.item)

    def get_absolute_url(self):
        return reverse('me2ushop:product_images', kwargs={'slug': self.item.slug})


#
class VariationsManager(models.Manager):
    def all(self):
        return super(VariationsManager, self).filter(active=True)

    def sizes(self):
        return self.all().filter(category='size')

    def colors(self):
        return self.all().filter(category='color')


VAR_CATEGORIES = (
    ('size', 'size'),
    ('color', 'color'),
    ('package', 'package'),
)


class ProductDetail(CreationModificationDateMixin):
    """    The ``ProductDetail`` model represents information unique to a
    specific product. This is a generic design that can be used
    to extend the information contained in the ``Product`` model with
    specific, extra details.
    """
    product = models.ForeignKey("Product", related_name="Details", on_delete=models.CASCADE)
    attribute = models.ForeignKey('ProductAttribute', on_delete=models.CASCADE)
    value = models.CharField(max_length=500)
    description = models.TextField(blank=True)

    def __str__(self):
        return u'%s: %s - %s' % (self.product,
                                 self.attribute,
                                 self.value)


class ProductAttribute(CreationModificationDateMixin):
    """
    The ``ProductAttribute`` model represents a class of feature found
    across a set of products. It does not store any data values related to the attribute,
    but only describes what kind of a product feature we are trying to capture. Possible attributes include things such 4
    as materials, colors, sizes, and many, many more.
    """

    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    def __str__(self):
        return u'%s' % self.name


class WishList(CreationModificationDateMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.product.title)


class StatusCode(CreationModificationDateMixin):
    """
    The StatusCode model represents the status of an order in the
    system.
    """
    NEW = 10
    PAID = 20
    PROCESSING = 30
    SENT = 40
    CANCELLED = 50
    IN_TRANSIT = 60
    DELIVERED = 70

    STATUSES = ((NEW, "New"),
                (PAID, "Paid"),
                (PROCESSING, "Processing"),
                (SENT, "Sent"),
                (CANCELLED, "Cancelled"),
                (IN_TRANSIT, "in_transit"),
                (DELIVERED, "Delivered"),
                )

    short_name = models.IntegerField(choices=STATUSES, default=NEW)
    name = models.CharField(max_length=300)
    description = models.TextField()

    def __str__(self):
        return str(self.short_name)


class OrderItem(CreationModificationDateMixin):
    # from stats.models import ProductView
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
    customer_order = models.ForeignKey('Order', blank=True, null=True, on_delete=models.SET_NULL)
    cart_id = models.CharField(max_length=40, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    status_code = models.ForeignKey('StatusCode', on_delete=models.SET_NULL, blank=True, null=True)
    order_received = models.BooleanField(default=False)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.PROTECT, unique=False, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    comments = models.TextField(blank=True)
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

    def total_items_ordered(self):
        # total = self.orderitem_set.all().count()
        total = 0
        for order_item in self.filter(ordered=True):
            total += order_item.quantity

        return total

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


class Order(CreationModificationDateMixin):
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = ((NEW, 'New'), (PAID, 'Paid'), (DONE, 'Done'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True,
                                 db_index=True)
    cart_id = models.CharField(max_length=40, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    status_code = models.ForeignKey('StatusCode', on_delete=models.SET_NULL, blank=True, null=True)
    items = models.ManyToManyField('OrderItem')
    ref_code = models.CharField(max_length=20)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    payment = models.CharField(max_length=2, blank=True, null=True)
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
    comments = models.TextField(blank=True)

    last_spoken_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="cs_chats",
                                       on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-modified']

    def __str__(self):
        return str(self.id)

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
        return str(self.user.username)

    def get_images(self):
        return self.product.productimage_set.all()


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
        return "%s, %s, %s, %s, %s" % (self.street_address, self.country, self.city, self.zip, self.phone)

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
# class OrderAnonymous(OrderInfo): from stats.models import ProductView cart_id = models.ForeignKey(ProductView,
# max_length=70, blank=True, null=True, on_delete=models.CASCADE) billing_address = models.ForeignKey('Address',
# related_name='billing_address_anonymous', on_delete=models.SET_NULL, blank=True, null=True) shipping_address =
# models.ForeignKey('Address', related_name='shipping_address_anonymous', on_delete=models.SET_NULL, blank=True,
# null=True)
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
