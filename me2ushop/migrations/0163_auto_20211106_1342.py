# Generated by Django 3.1.1 on 2021-11-06 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0162_auto_20211106_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('S', 'Stripe'), ('P', 'Paypal'), ('M', 'M-Pesa')], max_length=2),
        ),
        migrations.AlterField(
            model_name='nameyourprice',
            name='accepted',
            field=models.BooleanField(blank=True),
        ),
    ]
