# Generated by Django 3.0.7 on 2020-08-29 00:14

import django.core.validators
from django.db import migrations, models
import django_countries.fields
import stdimage.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(max_length=100)),
                ('apartment_address', models.CharField(max_length=100)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('city', models.CharField(max_length=60)),
                ('zip', models.CharField(max_length=10)),
                ('address_type', models.CharField(choices=[('B', 'Billing'), ('S', 'Shipping')], max_length=1)),
                ('payment_option', models.CharField(choices=[('C', 'Cash On Delivery'), ('P', 'Paypal'), ('S', 'Stripe'), ('M', 'M-Pesa'), ('D', 'Debit Card')], max_length=2)),
                ('default', models.BooleanField(default=False)),
                ('name', models.CharField(blank=True, max_length=60, null=True)),
                ('email', models.EmailField(blank=True, max_length=50, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('date_updated', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
                'ordering': ['-date_updated'],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, default=20, max_digits=9)),
                ('valid', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(10, 'New'), (20, 'Paid'), (30, 'Done')], default=10)),
                ('ref_code', models.CharField(max_length=20)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('order_date', models.DateTimeField(auto_now=True)),
                ('ordered', models.BooleanField(default=False)),
                ('being_delivered', models.BooleanField(default=False)),
                ('received', models.BooleanField(default=False)),
                ('refund_requested', models.BooleanField(default=False)),
                ('refund_granted', models.BooleanField(default=False)),
                ('email', models.EmailField(blank=True, max_length=50, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('name', models.CharField(blank=True, max_length=60, null=True)),
                ('billing_address1', models.CharField(max_length=60)),
                ('billing_address2', models.CharField(blank=True, max_length=60)),
                ('billing_zip_code', models.CharField(max_length=12)),
                ('billing_country', models.CharField(max_length=3)),
                ('billing_city', models.CharField(blank=True, max_length=12, null=True)),
                ('shipping_address1', models.CharField(max_length=60)),
                ('shipping_address2', models.CharField(blank=True, max_length=60)),
                ('shipping_zip_code', models.CharField(max_length=12)),
                ('shipping_country', models.CharField(max_length=3)),
                ('shipping_city', models.CharField(blank=True, max_length=12, null=True)),
            ],
            options={
                'ordering': ['-order_date'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_ordered', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(choices=[(10, 'New'), (20, 'Processing'), (30, 'Sent'), (40, 'Cancelled')], default=10)),
                ('ordered', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'ordering': ['-date_added'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(help_text='Unique value for product page URL, created from the product title.', unique=True)),
                ('brand', models.CharField(help_text='Your store name', max_length=50)),
                ('stock', models.IntegerField(default=0)),
                ('in_stock', models.BooleanField(blank=True, default=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('discount_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, null=True)),
                ('made_in_africa', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_bestseller', models.BooleanField(default=False)),
                ('is_featured', models.BooleanField(default=False)),
                ('description', models.TextField()),
                ('additional_information', models.TextField(blank=True, null=True)),
                ('meta_keywords', models.CharField(help_text='Comma-delimited set of SEO keywords that summarize the type of product above max 4 words', max_length=100, verbose_name='Meta Keywords')),
                ('meta_description', models.CharField(help_text='help sellers get your product easily. Give a simple short description about the page content you have added. This information makes iteasy for customers to get your product and offers an overview of it', max_length=255, verbose_name='Meta Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category_choice', models.CharField(choices=[('At', 'Arts, Crafts'), ('Bk', 'Books'), ('Bb', 'Baby Care'), ('Be', 'Beautiful 2'), ('Ca', 'Camera & Photo'), ('S', 'Shirt'), ('Sw', 'Sport wear'), ('Ow', 'Outwear'), ('Am', 'Automotive & Motorcycle'), ('Ca', 'Cell Phones & Accessories'), ('El', 'Electronics'), ('Fa', 'Fashion'), ('Fu', 'Furniture'), ('So', 'Sokoni'), ('Wo', 'Women Fashion')], help_text='Choose the main category for the product', max_length=2)),
                ('label', models.CharField(blank=True, choices=[('P', 'primary'), ('S', 'secondary'), ('D', 'danger')], help_text='tags the product NEW upon upload for the next 24 hoursprimary blue, danger red, secondary purple', max_length=1, null=True)),
            ],
            options={
                'verbose_name_plural': 'Products',
                'db_table': 'Products',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', stdimage.models.StdImageField(blank=True, null=True, upload_to='images/products')),
                ('in_display', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('-in_display',),
            },
        ),
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('rating', models.PositiveSmallIntegerField(choices=[(5, 5), (4, 4), (3, 3), (2, 2), (1, 1)], default=5)),
                ('is_approved', models.BooleanField(default=True)),
                ('content', models.TextField()),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RequestRefund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('accepted', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254)),
                ('ref_code', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='StripePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_charge_id', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=9)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
