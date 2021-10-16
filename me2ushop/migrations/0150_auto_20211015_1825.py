# Generated by Django 3.1.1 on 2021-10-15 16:25

from django.db import migrations


def migrate_products(apps, schema_editor):
    Product = apps.get_model('me2ushop', 'Product')

    for product in Product.objects.all():
        print('product:', product.shipping_status)
        if not product.shipping_status:
            print('nos shipping')
            product.shipping_status = 'Cd'
            product.save()
        product.save()


class Migration(migrations.Migration):
    dependencies = [
        ('me2ushop', '0149_auto_20211015_1722'),
    ]

    operations = [
        migrations.RunPython(migrate_products, migrations.RunPython.noop)
        ]
