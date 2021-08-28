# Generated by Django 3.1.1 on 2021-08-08 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0138_auto_20210808_2341'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductDetail',
            new_name='ProductVariations',
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('P', 'Paypal'), ('M', 'M-Pesa'), ('S', 'Stripe')], max_length=2),
        ),
    ]
