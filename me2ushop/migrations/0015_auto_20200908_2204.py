# Generated by Django 3.1.1 on 2020-09-08 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0014_auto_20200904_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('M', 'M-Pesa'), ('P', 'Paypal'), ('D', 'Debit Card'), ('C', 'Cash On Delivery'), ('S', 'Stripe')], max_length=2),
        ),
    ]
