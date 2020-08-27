from me2ushop import models
from categories.models import Category
from django.contrib.flatpages.models import FlatPage
from django.contrib.sitemaps import Sitemap


class ProductSitemap(Sitemap):
    def items(self):
        return models.Product.active.all()


class CategorySitemap(Sitemap):
    def items(self):
        return Category.active.all()


class FlatPageSitemap(Sitemap):
    def items(self):
        return FlatPage.objects.all()


SITEMAPS = {'categories': CategorySitemap,
            'products': ProductSitemap,
            'flatpages': FlatPageSitemap}
