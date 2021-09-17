import itertools

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.shortcuts import reverse
from django.utils.text import slugify
from django_countries.fields import CountryField
from stdimage import StdImageField
from django.utils.translation import ugettext_lazy as _
from utils.models import CreationModificationDateMixin
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey, TreeManyToManyField

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


class ActiveCategoryManager(models.Manager):
    def get_query_set(self):
        return super(ActiveCategoryManager, self).get_query_set().filter(is_active=True)


class CategoryManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Category(models.Model):
    category_name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    slug = models.SlugField(unique=True,
                            max_length=50,
                            help_text='Unique value for product page URL, created from name.')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    image = StdImageField(upload_to='images/category', blank=True, null=True, variations={
        'medium': (340, 300),

    }, delete_orphans=True)
    meta_keywords = models.CharField("Meta Keywords",
                                     max_length=255,
                                     help_text='Comma-delimited set of SEO keywords for meta tag')
    meta_description = models.CharField("Meta Description",

                                        max_length=255,
                                        help_text='Content for description meta tag')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # objects = models.Manager()
    objects = CategoryManager()
    active = ActiveCategoryManager()

    def __str__(self):
        return self.category_name

    # The natural_key method should return a tuple, not a string.
    def natural_key(self):
        return (self.slug,)

    class Meta:
        db_table = 'ProductCategories'
        ordering = ['category_name']
        verbose_name_plural = 'ProductCategories'

    def get_absolute_url(self):
        return reverse('categories:categoryView', kwargs={'slug': self.slug})

    def get_absolute_africa_made_url(self):
        return reverse('categories:categoryView_africa_made', kwargs={'slug': self.slug})


class ActiveDepartmentManager(models.Manager):
    def get_query_set(self):
        return super(ActiveDepartmentManager, self).get_query_set().filter(is_active=True)


class DepartmentManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Department(MPTTModel, CreationModificationDateMixin):
    parent = TreeForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, related_name='children')
    category_name = models.CharField(_("Title"), max_length=200)
    # sub_category_name = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE)
    icon_url = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(unique=True,
                            editable=False,
                            max_length=50,
                            help_text='Unique value for product page URL, created from name.')
    description = models.TextField()
    is_active = models.BooleanField(default=False, editable=False)
    is_bestselling = models.BooleanField(default=False)
    image = StdImageField(upload_to='images/category', blank=True, null=True, variations={
        'medium': (340, 300),

    }, delete_orphans=True)

    icon_image = StdImageField(upload_to='images/category/icons', blank=True, null=True)
    meta_keywords = models.CharField("Meta Keywords",
                                     max_length=255,
                                     help_text='Comma-delimited set of SEO keywords for meta tag')
    meta_description = models.CharField("Meta Description",

                                        max_length=255,
                                        help_text='Content for description meta tag')

    # objects = models.Manager()
    objects = DepartmentManager()
    active = ActiveDepartmentManager()

    class Meta:
        ordering = ['tree_id', 'lft']
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

    # def __str__(self):
    #     return str(self.category_name)

    def __str__(self):
        full_path = [self.category_name]
        k = self.parent
        while k is not None:
            full_path.append(k.category_name)
            k = k.parent
        return ' / '.join(full_path[::-1])

    # The natural_key method should return a tuple, not a string.
    def natural_key(self):
        return (self.slug,)

    def get_absolute_url(self):
        return reverse('categories:categoryView', kwargs={'slug': self.slug})

    def get_absolute_africa_made_url(self):
        return reverse('categories:categoryView_africa_made', kwargs={'slug': self.slug})

    def get_products(self):
        if self.pk:
            return self.product_set.filter(is_active=True)
        else:
            return None

    def _generate_slug(self):
        # max_length = self._meta.get_field('slug').max_length
        value = self.category_name
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Department.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        return slug_candidate

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = self._generate_slug()

        if self.pk:
            products = self.product_set.filter(is_active=True).first()
            # print('products category:', products)
            if products:
                self.is_active = True
            else:
                self.is_active = False

        super().save(*args, **kwargs)
