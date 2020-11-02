# Generated by Django 3.1.1 on 2020-10-07 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0006_auto_20201007_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_link_url',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('P', 'Paypal'), ('D', 'Debit Card'), ('C', 'Cash On Delivery'), ('M', 'M-Pesa'), ('S', 'Stripe')], max_length=2),
        ),
    ]
