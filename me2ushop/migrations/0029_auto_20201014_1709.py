# Generated by Django 3.1.1 on 2020-10-14 15:09

from django.db import migrations, models
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0028_auto_20201014_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('M', 'M-Pesa'), ('D', 'Debit Card'), ('P', 'Paypal'), ('S', 'Stripe'), ('C', 'Cash On Delivery')], max_length=2),
        ),
        migrations.AlterField(
            model_name='brand',
            name='image',
            field=stdimage.models.StdImageField(blank=True, default='images/brands/brand_background/default.jpg', help_text='wallpaper for your store', null=True, upload_to='images/brands/brand_background'),
        ),
    ]
