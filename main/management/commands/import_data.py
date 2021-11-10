from collections import Counter
import csv
import os.path
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from me2ushop import models
from categories.models import Category, Department


class Command(BaseCommand):
    help = 'Import Products in Me2ushop'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=open)
        parser.add_argument("image_basedir", type=str)

    def handle(self, *args, **options):
        self.stdout.write('importing products')
        c = Counter()
        reader = csv.DictReader(options.pop("csvfile"))

        for row in reader:
            product, created = models.Product.objects.get_or_create(
                title=row['title'], price=row['price']
            )
            product.description = row['description']
            product.slug = slugify(row['title'])

            for import_category in row['product_categories'].split("|"):
                category, category_created = Department.objects.get_or_create(
                    category_name=import_category
                )
                category.slug = slugify(import_category)
                category.save()

                product.product_categories.add(category)
                # counter
                c["product_categories"] += 1
                if category_created:
                    c['category_created'] += 1

            with open(os.path.join(options["image_basedir"], row["image_filename"], ), "rb", ) as f:
                image = models.ProductImage(item=product,
                                            image=ImageFile(f, name=row["image_filename"]), )
                image.save()
                c['images'] += 1

            product.save()
            c["products"] += 1
            if created:
                c["products_created"] += 1

        self.stdout.write(
            "Categories processed=%d (created=%d)" % (c['categories'], c['categories_created'])
        )
        self.stdout.write(
            "Products processed=%d (created=%d)" % (c['products'], c['products_created'])
        )
        self.stdout.write(
            "Images processed=%d" % (c['images'])
        )
