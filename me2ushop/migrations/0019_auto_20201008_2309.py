# Generated by Django 3.1.1 on 2020-10-08 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0018_auto_20201008_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('D', 'Debit Card'), ('P', 'Paypal'), ('M', 'M-Pesa'), ('S', 'Stripe'), ('C', 'Cash On Delivery')], max_length=2),
        ),
    ]
