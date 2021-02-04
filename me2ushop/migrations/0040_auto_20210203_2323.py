# Generated by Django 3.1.1 on 2021-02-03 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0039_auto_20210203_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('S', 'Stripe'), ('M', 'M-Pesa'), ('C', 'Cash On Delivery'), ('D', 'Debit Card'), ('P', 'Paypal')], max_length=2),
        ),
        migrations.AlterField(
            model_name='product',
            name='condition',
            field=models.CharField(choices=[('U', 'Used'), ('R', 'Refurbished'), ('N', 'New')], help_text='Choose the current condition for the product', max_length=2),
        ),
    ]
