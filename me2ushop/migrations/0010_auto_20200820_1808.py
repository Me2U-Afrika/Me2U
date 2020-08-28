# Generated by Django 3.0.7 on 2020-08-20 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0009_auto_20200819_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('C', 'Cash On Delivery'), ('D', 'Debit Card'), ('P', 'Paypal'), ('S', 'Stripe'), ('M', 'M-Pesa')], max_length=2),
        ),
        migrations.AlterField(
            model_name='product',
            name='meta_description',
            field=models.CharField(help_text='help sellers get your product easily. Give a simple short description about the page content you have added. This information makes iteasy for customers to get your product and offers an overview of it', max_length=255, verbose_name='Meta Description'),
        ),
    ]