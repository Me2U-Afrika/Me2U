# Generated by Django 3.1.1 on 2020-10-17 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0031_auto_20201016_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('D', 'Debit Card'), ('P', 'Paypal'), ('S', 'Stripe'), ('C', 'Cash On Delivery'), ('M', 'M-Pesa')], max_length=2),
        ),
    ]
