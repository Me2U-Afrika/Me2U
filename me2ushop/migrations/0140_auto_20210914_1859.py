# Generated by Django 3.1.1 on 2021-09-14 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0139_auto_20210808_2355'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='subscription_status',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('S', 'Stripe'), ('P', 'Paypal'), ('M', 'M-Pesa')], max_length=2),
        ),
    ]
