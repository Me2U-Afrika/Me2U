# Generated by Django 3.1.1 on 2020-10-23 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0034_auto_20201023_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='added_to_wishlist',
        ),
        migrations.AddField(
            model_name='wishlist',
            name='added_to_wishlist',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('C', 'Cash On Delivery'), ('P', 'Paypal'), ('M', 'M-Pesa'), ('S', 'Stripe'), ('D', 'Debit Card')], max_length=2),
        ),
    ]
