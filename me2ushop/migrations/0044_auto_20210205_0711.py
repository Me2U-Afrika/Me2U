# Generated by Django 3.1.1 on 2021-02-05 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0043_auto_20210204_0302'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brand',
            name='telegram',
        ),
        migrations.AddField(
            model_name='brand',
            name='twitter',
            field=models.CharField(blank=True, help_text='Do you have a Telegram Channel. Copy paste your page link here. e.g.. https://t.me/me2uafrika', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('C', 'Cash On Delivery'), ('D', 'Debit Card'), ('S', 'Stripe'), ('M', 'M-Pesa'), ('P', 'Paypal')], max_length=2),
        ),
        migrations.AlterField(
            model_name='brand',
            name='website_link',
            field=models.CharField(blank=True, help_text='If you have a website by which buyers can find out more about your services.e.g. https://www.facebook.com', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='condition',
            field=models.CharField(choices=[('U', 'Used'), ('R', 'Refurbished'), ('N', 'New')], help_text='Choose the current condition for the product', max_length=2),
        ),
    ]
