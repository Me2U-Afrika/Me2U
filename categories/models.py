from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.shortcuts import reverse
from django_countries.fields import CountryField
from stdimage import StdImageField

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


class CategoryTagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Category(models.Model):
    category_name = models.CharField(max_length=50)
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

    objects = models.Manager()
    active = ActiveCategoryManager()

    def __str__(self):
        return self.category_name

    def natural_key(self):
        return self.slug

    class Meta:
        db_table = 'ProductCategories'
        ordering = ['category_name']
        verbose_name_plural = 'ProductCategories'

    def get_absolute_url(self):
        return reverse('categories:categoryView', kwargs={'slug': self.slug})

    def get_absolute_africa_made_url(self):
        return reverse('categories:categoryView_africa_made', kwargs={'slug': self.slug})
