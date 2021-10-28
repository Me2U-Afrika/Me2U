import collections
import decimal
import itertools

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.core.cache import cache
from django.core.validators import MinValueValidator
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from django_countries.fields import CountryField
from stdimage import StdImageField
from tagging.registry import register

from categories.models import Department
from users.models import STATUSES, UNDER_REVIEW
from utils.models import CreationModificationDateMixin
from djangorave.models import DRPaymentTypeModel

from django.utils.safestring import mark_safe

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

}

SUBSCRIPTION_TYPE_CHOICE = (
    ('Fr', 'Free'),
    ('St', 'Standard'),
    ('Bs', 'Basic'),
    ('Pr', 'Premium')
)

BUSINESS_TYPE_CHOICE = (
    ('Co', 'Company'),
    ('Sol', 'Sole Proprietorship/Personal')
)

CONDITION_CHOICES = {

    ('N', "New"),
    ('R', "Refurbished"),
    ('U', "Used"),

}
SHIPPING_CAPABILITY = (
    ('Cd', 'Can Ship Abroad and Deliver Locally'),
    ('Cl', 'Can Deliver Locally(Within your country)'),
    ('Co', 'Not Able to Deliver')
)
from django_countries import Countries


class AfrikanCountries(Countries):
    only = [
        'DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD',
        'KM', 'CG', 'CD', 'CI', 'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA',
        'GM', 'GH', 'GN', 'GW', 'KE', 'LS', 'LR', 'LY', 'MG', 'ML',
        'MW', 'MR', 'MU', 'YT', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RE',
        'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'SZ',
        'TZ', 'TG', 'TN', 'UG', 'EH', 'ZM', 'ZW'
    ]


class ContactSupplier(CreationModificationDateMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        return self.user.username


class ActiveBrandManager(models.Manager):
    def all(self):
        return super(ActiveBrandManager, self).all().filter(is_active=True)


class Brand(CreationModificationDateMixin):
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(default='',
                            editable=False,
                            blank=True,
                            null=True,
                            max_length=255)
    title = models.CharField(max_length=200, unique=True, help_text='Unique business title to identify Your store and '
                                                                    'your product line')
    website_link = models.CharField(max_length=255, blank=True, null=True,
                                    help_text='If you have a website by which buyers can find out more about your '
                                              'services.e.g. https://www.facebook.com')
    facebook = models.CharField(max_length=255, blank=True, null=True,
                                help_text='Do you have a facebook page. Copy paste your page link here '
                                          'e.g..https://www.facebook.com/Me2UAfrika')
    instagram = models.CharField(max_length=255, blank=True, null=True,
                                 help_text='Do you have a instagram page. Copy paste your page link here '
                                           'eg..https://www.instagram.com/me2u_afrika/')
    twitter = models.CharField(max_length=255, blank=True, null=True,
                               help_text='Do you have a Telegram Channel. Copy paste your page link here. '
                                         'e.g..https://t.me/me2uafrika')

    business_phone = models.CharField(max_length=20, blank=True, null=True,
                                      help_text='Business Phone Number . i.e +250785....')
    business_email = models.EmailField(blank=True, null=True, max_length=254,
                                       help_text='Business Phone Number . i.e +250785....')
    contact_person = models.CharField(max_length=255, blank=True, null=True,
                                      help_text="Contact person name who will receive inquiries")
    business_description = models.TextField(help_text="Tell us what you do and the kind of products you sell")

    business_type = models.CharField(choices=BUSINESS_TYPE_CHOICE, max_length=4)
    country = CountryField(multiple=False)
    address1 = models.CharField(max_length=100, blank=True, null=True)
    address2 = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=12, blank=True, null=True)
    subscription_plan = models.ForeignKey(DRPaymentTypeModel, blank=True, null=True, on_delete=models.SET_NULL,
                                          help_text='Select a monthly recurring subscription fees')
    # subscription_type = models.CharField(max_length=2, choices=SUBSCRIPTION_TYPE_CHOICE,
    #                                      help_text='Select a monthly recurring subscription fees')
    subscription_reference = models.CharField(max_length=200, blank=True, null=True)
    subscription_status = models.BooleanField(default=True, blank=True, null=True)
    # shipping_status = models.CharField(choices=SHIPPING_CAPABILITY, max_length=2, default='Cd', blank=True, null=True,
    #                                    help_text='Is Your company able to ship or deliver your products once they '
    #                                              'buyers order online?')
    valid_payment_method = models.BooleanField(default=False, null=True, blank=True)
    is_active = models.BooleanField(editable=False, default=True)
    is_featured = models.BooleanField(default=False, blank=True, null=True)
    image = StdImageField(upload_to='images/brands/brand_background', blank=True, null=True,
                          help_text='wallpaper for your store.Leave blank if you don\'t have one',
                          default='images/brands/brand_background/default.jpg', variations={
            'large': (415, 470,), }, delete_orphans=True)

    logo = StdImageField(upload_to='images/brands/brand_logo', blank=True, null=True,
                         help_text='logo for your store, Leave blank if you don\'t have one',
                         variations={
                             'medium': (150, 150, True),

                         }, delete_orphans=True)
    application_status = models.IntegerField(choices=STATUSES, default=UNDER_REVIEW, blank=True, null=True)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('sellers:seller_home', kwargs={'slug': self.slug})

    def get_backstore_url(self):
        return reverse('sellers:seller_home', kwargs={'slug': self.slug})

    def get_frontstore_url(self):
        return reverse('me2ushop:seller_page', kwargs={'slug': self.slug})

    def get_brandupdate_url(self):
        return reverse('me2ushop:brand_update', kwargs={'pk': self.pk})

    def _generate_slug(self):
        value = self.title
        slug_original = slugify(value, allow_unicode=True)

        slug_candidate = '{}'.format(slug_original)

        return slug_candidate

    def save(self, *args, **kwargs):
        if not self.pk or self.slug == '':
            self.slug = self._generate_slug()

        if self.subscription_status and 10 < self.application_status < 40:
            self.is_active = True
        else:
            self.is_active = False

        if self.product_set.all():
            for product in self.product_set.all():
                product.save()

        cache.delete('brand-%s' % self.slug)

        super().save(*args, **kwargs)


class ActiveProductManager(models.Manager):
    def all(self):
        return super(ActiveProductManager, self).all().filter(is_active=True, not_active=False).prefetch_related(
            'productimage_set')


class ProductManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Unitofmeasure(CreationModificationDateMixin):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(CreationModificationDateMixin):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True,
                            default='',
                            editable=False,
                            max_length=300
                            )
    brand_name = models.ForeignKey('Brand', on_delete=models.SET_NULL, blank=True, null=True,
                                   help_text='Your store name')
    stock = models.IntegerField(default=1)
    unit_measure = models.ForeignKey(Unitofmeasure, blank=True, null=True, on_delete=models.SET_NULL)
    view_count = models.IntegerField(default=0, editable=False)
    sku = models.CharField(max_length=120, default='',
                           editable=False, )
    in_stock = models.BooleanField(default=True, editable=False)
    min_amount = models.IntegerField(default=1, blank=True, help_text="What is the minimum order units required for "
                                                                      "this item?")
    max_amount = models.IntegerField(blank=True, null=True, help_text="What is the maximum order units required for "
                                                                      "this item?")

    price = models.DecimalField(max_digits=9, decimal_places=2, default=0,
                                help_text="What is the price of one piece of this item?"
                                          "Please note that the default currency is "
                                          "USD. Converty your product price to "
                                          "US dollar before listing.")
    discount_price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(1)],
                                         blank=True, null=True,
                                         help_text="Please note that the default currency is "
                                                   "USD. Converty your product price to "
                                                   "US Dollar before listing")

    is_active = models.BooleanField(default=True, editable=False)
    not_active = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_bestrated = models.BooleanField(default=False)

    description = RichTextField(max_length=400, config_name='Special')

    additional_information = RichTextUploadingField(blank=True, null=True,
                                                    help_text='Provide additional information about '
                                                              'your product. Buyers mostly buy from'
                                                              ' well detailed products and '
                                                              'specifications')
    shipping_status = models.CharField(choices=SHIPPING_CAPABILITY, max_length=2, default='Cd', blank=True, null=True,
                                       help_text='Is Your company able to ship or deliver this product once they '
                                                 'buyers order online?')
    meta_keywords = models.CharField("Meta Keywords",
                                     max_length=100,
                                     help_text='Comma-delimited set of SEO keywords that summarize the type of '
                                               'product above max 4 words. This keywords will help buyers find your '
                                               'product easily. Read more https://ads.google.com/home/tools/keyword'
                                               '-planner/')
    meta_description = models.CharField("Meta Description",
                                        max_length=255,
                                        help_text='Give a simple short '
                                                  'description on the information you have provided on the page this '
                                                  'page. i.e This product is used '
                                                  'for cleaning, cooking and it was recently released by it\'s '
                                                  'manufacturer. Google uses this keywords and description to index '
                                                  'your product for it to be found easily '
                                        )

    product_categories = models.ManyToManyField(Department,

                                                help_text='Check the box of the category where your product belongs. '
                                                          'Please note that different categories attract different Ad '
                                                          'charges. Be specific to one or two categories where your '
                                                          'product '
                                                          'belongs on the provided tree. Contact us for help')

    objects = ProductManager()
    active = ActiveProductManager()

    def __str__(self):
        return str(self.title)

    def natural_key(self):
        return (self.slug,)

    class Meta:
        db_table = 'Products'
        ordering = ['-modified']
        verbose_name_plural = 'Products'

    def get_category(self):
        pass

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
        if self.discount_price and self.price > 0:
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
        else:
            return self.get_images()[0]

    def image_tag(self):
        image = self.get_image_in_display()
        if image:
            return mark_safe('<img src="{}" height="50"/>'.format(image.image.thumbnail.url))
        else:
            return ""

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
        from django.db.models import Q

        category = self.product_categories
        name = self.title
        # print('category:', category)
        # print('name:', name)
        # print('other sellers:', users)
        # print('self', self.slug)
        words = _prepare_words(self.title)
        # print('words:', words)

        for word in words:
            products = Product.active.filter(
                Q(title__icontains=self) |
                Q(title__startswith=self) |
                Q(title__icontains=word) |
                Q(title__startswith=word) |
                Q(title__endswith=self) |
                Q(title__endswith=word)
            ).exclude(slug=self.slug)
            # print('from sellers', products)
            return products

    def cross_sells_hybrid(self):
        from users.models import User

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
            most_products.append(product)

        return most_products

    def _generate_slug(self):
        value = self.title
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Product.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        return slug_candidate

    def _generate_sku(self):

        brand = str(self.brand_name)[:3]
        title = str(self.title)[:3]
        created = str(self.created)

        sku = '{}-{}-{}'.format(brand, title, created)

        for i in itertools.count(1):
            if not Product.objects.filter(sku=sku).exists():
                break
            sku = '{}-{}-{}-{}'.format(brand, title, created, i)
        return sku

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = self._generate_slug()
            self.sku = self._generate_sku()

        if self.shipping_status == '':
            self.shipping_status = 'Cd'

        self.in_stock = True
        self.is_active = True

        if self.stock < self.min_amount:
            # print('we came to check stock')
            self.in_stock = False
            self.is_active = False

        if self.brand_name:
            if self.brand_name.is_active and self.in_stock:
                self.is_active = True
            else:
                self.is_active = False
        else:
            self.is_active = False

        image = self.productimage_set.filter(in_display=True)

        # print('image', image.exists())

        if image.exists() and self.is_active:
            self.is_active = True

        else:
            self.is_active = False

        if self.not_active:
            self.is_active = False

        if self.discount_price and self.price < 1 or self.discount_price == self.price:
            self.price = self.discount_price
            self.discount_price = None

        if not self.is_active:
            if self.banner_set.all():
                for banner in self.banner_set.all():
                    banner.save()

        cache.delete('product-%s' % self.slug)

        super().save(*args, **kwargs)


# REGISTER PRODUCT MODEL AS A TAG
register(Product)


class ProductCustomizations(CreationModificationDateMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    min_order = models.IntegerField(default=1)
    max_order = models.IntegerField(blank=True, null=True)
    customization_price = models.DecimalField(max_digits=9, blank=True, null=True, decimal_places=2)
    customization_discount_price = models.DecimalField(max_digits=9, blank=True, null=True, decimal_places=2)

    def __str__(self):
        return self.name


class DisplayImageManager(models.Manager):
    def get_query_set(self):
        return super(DisplayImageManager, self).get_query_set().filter(in_display=True)


class ProductImage(CreationModificationDateMixin):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Image title")
    image = StdImageField(upload_to='images/products', variations={
        'thumbnail': (180, 180),
        'large': (585, 585),

    }, delete_orphans=True)

    in_display = models.BooleanField(default=True)

    objects = ProductManager()
    displayed = DisplayImageManager()

    class Meta:
        ordering = ('-in_display',)

    def __str__(self):
        if self.title:
            return str(self.title)
        return str(self.item)

    def natural_key(self):
        return (self.item.slug,)

    def get_absolute_url(self):
        return reverse('me2ushop:product_images', kwargs={'slug': self.item.slug})

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s" height="80"/>' % self.image.thumbnail.url)
        else:
            return ""

    # thumbnail_tag.short_description = "Thumbnail"

    def save(self, *args, **kwargs):
        cache.delete('productimage-%s' % self.pk)

        super().save(*args, **kwargs)


#
# class VariationsManager(models.Manager):
#     def all(self):
#         return super(VariationsManager, self).filter(is_active=True)
#
#     def sizes(self):
#         return self.all().filter(variation_category='size')
#
#     def colors(self):
#         return self.all().filter(variation_category='color')
#
#
# VAR_CATEGORIES = (
#     ('size', 'size'),
#     ('color', 'color'),
#     ('package', 'package'),
# )
#

# class VariationCategory(CreationModificationDateMixin):
#     variation_name = models.CharField(max_length=200, unique=True)
#
#     def __str__(self):
#         return self.variation_name
#
#
# class Variation(CreationModificationDateMixin):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
#     title = models.CharField(max_length=100, blank=True, null=True,
#                              help_text="Title for this product variant")
#     variation_category = models.ForeignKey(VariationCategory, on_delete=models.CASCADE)
#     variation_value = models.CharField(max_length=200)
#     price = models.DecimalField(max_digits=9, null=True, blank=True, decimal_places=2, default=0,
#                                 help_text="Please note that the default currency is "
#                                           "USD. Converty your product price to "
#                                           "US dollar before listing")
#
#     discount_price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(1)],
#                                          blank=True, null=True,
#                                          help_text="Please note that the default currency is "
#                                                    "USD. Converty your product price to "
#                                                    "US Dollar before listing")
#     image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, blank=True, null=True)
#
#     is_active = models.BooleanField(default=True)
#
#     stock = models.IntegerField(default=1, blank=True, null=True)
#
#     objects = VariationsManager()
#
#     class Meta:
#         unique_together = (
#             ('variation_category', 'variation_value')
#         )
#
#     def __str__(self):
#         return u'%s - %s' % (self.variation_category, self.variation_value,)
#
#     def get_absolute_url(self):
#         return reverse('me2ushop:product', kwargs={'slug': self.product.slug})
#
#     def image_tag(self):
#         if self.image:
#             return mark_safe('<img src="{}" height="50"/>'.format(self.image.image.thumbnail.url))
#         else:
#             return ""


class Color(CreationModificationDateMixin):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


class Size(CreationModificationDateMixin):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


class ProductVariationsManager(models.Manager):
    def all(self):
        return super(ProductVariationsManager, self).all()

    def active(self):
        return self.all().filter(is_active=True)


class ProductVariationsQueryset(models.query.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class ActiveProductVariationsManager(models.Manager):
    def get_queryset(self):
        return ProductVariationsQueryset(self.model, using=self._db).active()


class ProductVariations(CreationModificationDateMixin):
    """    The ``ProductDetail`` model represents information unique to a
    specific product. This is a generic design that can be used
    to extend the information contained in the ``Product`` model with
    specific, extra details.
    """

    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    slug = models.SlugField(unique=True,
                            default='',
                            blank=True,
                            null=True,
                            editable=False,
                            max_length=300
                            )
    title = models.CharField(max_length=100, blank=True, null=True,
                             help_text="Title for this product variant")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True,
                              help_text="Add if your product comes in different colors")

    size = models.ForeignKey(Size, on_delete=models.CASCADE, blank=True, null=True,
                             help_text="Add if your product comes in different colors")

    sku = models.CharField(max_length=120, default='',
                           editable=False, )
    in_stock = models.BooleanField(default=True, editable=False)
    min_amount = models.IntegerField(default=1, blank=True, help_text="What is the minimum order units required for "
                                                                      "this item?")
    max_amount = models.IntegerField(blank=True, null=True, help_text="What is the maximum order units required for "
                                                                      "this item?")

    price = models.DecimalField(max_digits=9, null=True, blank=True, decimal_places=2, default=0,
                                help_text="If the above variables affect your original price, update price"
                                          "Note that the default currency is "
                                          "USD. Convert your product price to US dollar before listing")

    discount_price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(1)],
                                         blank=True, null=True,
                                         help_text="Note that the default currency is "
                                                   "USD. Convert your product price to "
                                                   "US Dollar before listing")
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, blank=True, null=True)

    stock = models.IntegerField(default=1, blank=True, null=True)
    is_active = models.BooleanField(default=True, editable=False)

    objects = ProductVariationsManager()
    active = ActiveProductVariationsManager()

    class Meta:
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return u'%s - %s - %s' % (self.product, self.color, self.size,)

    def get_absolute_url(self):
        return reverse('me2ushop:product', kwargs={'slug': self.product.slug})

    # def get_remove_cart_url(self):
    #     return reverse('me2ushop:remove_cart', kwargs={'slug': self.slug})

    # def get_add_cart_url(self):
    #     return reverse('me2ushop:add_cart', kwargs={'slug': self.slug})

    def get_image(self):
        return self.image.image.thumbnail.url

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.image.thumbnail.url))
        else:
            return ""

    def sale_price(self):
        if self.discount_price:
            return self.discount_price
        else:
            return self.price

    def _generate_sku(self):

        variant = None
        brand = str(self.product.brand_name)[:3]
        title = str(self.product.title)[:3]
        created = str(self.created)

        if self.size and self.color:
            variant = '{}-{}'.format(self.size, self.color)
        elif self.size:
            variant = '{}'.format(self.size)
        elif self.color:
            variant = '{}'.format(self.color)

        sku = '{}-{}-{}-{}'.format(brand, title, created, variant)

        for i in itertools.count(1):
            if not ProductVariations.objects.filter(sku=sku).exists():
                break
            sku = '{}-{}-{}-{}'.format(brand, title, created, variant, i)
        return sku

    def _generate_slug(self):
        variant = self.product.title
        if self.size and self.color:
            variant = '{}-{}-{}'.format(self.product.title, self.size, self.color)
        elif self.size:
            variant = '{}-{}'.format(self.product.title, self.size)
        elif self.color:
            variant = '{}-{}'.format(self.product.title, self.color)
        value = variant

        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Product.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        return slug_candidate

    def save(self, *args, **kwargs):
        if not self.pk or self.sku or self.slug:
            self.sku = self._generate_sku()
            self.slug = self._generate_slug()

        self.in_stock = True
        if self.stock:
            if self.stock < self.min_amount:
                print('we came to check stock on product variant')
                self.in_stock = False
                self.is_active = False
            else:
                self.is_active = True

        if self.discount_price and self.price < 1 or self.discount_price == self.price:
            self.price = self.discount_price
            self.discount_price = None

        cache.delete('product-%s' % self.product.slug)

        super().save(*args, **kwargs)


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


class Rentals(CreationModificationDateMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    book_start = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    book_end = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    rental_price_day = models.DecimalField(max_digits=9, decimal_places=2)
    discount_per_week = models.IntegerField(blank=True, null=True)
    discount_per_month = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return u'%s' % self.product


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
    NEW = 10
    ACCEPTED = 20
    SENT = 30
    CANCELLED = 40
    IN_TRANSIT = 45
    DELIVERED = 50

    STATUSES = ((NEW, "New"),
                (ACCEPTED, "Accepted"),
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
    variant = models.ForeignKey(ProductVariations, blank=True, null=True, on_delete=models.SET_NULL)
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
        if self.variant:
            return self.quantity * self.variant.price
        else:
            return self.quantity * self.item.price

    def get_total_discount_price(self):
        if self.variant:
            return self.quantity * self.variant.discount_price
        else:
            return self.quantity * self.item.discount_price

    def get_total_saved(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.variant:
            if self.variant.discount_price:
                return self.get_total_discount_price()
            else:
                return self.get_total_price()
        else:
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
    ref_code = models.CharField(max_length=200)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    payment = models.CharField(max_length=2, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(blank=True, null=True)
    refund_granted = models.BooleanField(blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    name = models.CharField(max_length=60, blank=True, null=True)
    billing_address1 = models.CharField(max_length=60)
    billing_address2 = models.CharField(max_length=60, blank=True)
    billing_zip_code = models.CharField(max_length=12)
    billing_country = models.CharField(max_length=3)
    billing_city = models.CharField(max_length=12, blank=True, null=True)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
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
    accepted = models.BooleanField(blank=True, null=True)
    # email = models.EmailField()
    ref_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.pk}"
