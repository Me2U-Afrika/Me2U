# Generated by Django 3.1.1 on 2020-10-23 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0036_auto_20201023_1452'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist',
            name='added',
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('C', 'Cash On Delivery'), ('M', 'M-Pesa'), ('D', 'Debit Card'), ('S', 'Stripe'), ('P', 'Paypal')], max_length=2),
        ),
    ]