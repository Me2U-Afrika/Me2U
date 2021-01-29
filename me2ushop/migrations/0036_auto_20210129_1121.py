# Generated by Django 3.1.1 on 2021-01-29 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0035_auto_20210129_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('S', 'Stripe'), ('M', 'M-Pesa'), ('D', 'Debit Card'), ('C', 'Cash On Delivery'), ('P', 'Paypal')], max_length=2),
        ),
        migrations.AlterField(
            model_name='product',
            name='condition',
            field=models.CharField(choices=[('N', 'New'), ('U', 'Used'), ('R', 'Refurbished')], help_text='Choose the current condition for the product', max_length=2),
        ),
    ]
