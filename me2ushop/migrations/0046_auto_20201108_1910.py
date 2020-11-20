# Generated by Django 3.1.1 on 2020-11-08 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0045_auto_20201108_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('P', 'Paypal'), ('C', 'Cash On Delivery'), ('D', 'Debit Card'), ('S', 'Stripe'), ('M', 'M-Pesa')], max_length=2),
        ),
    ]