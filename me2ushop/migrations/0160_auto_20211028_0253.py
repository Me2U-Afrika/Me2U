# Generated by Django 3.1.1 on 2021-10-28 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0159_auto_20211025_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('M', 'M-Pesa'), ('S', 'Stripe'), ('P', 'Paypal')], max_length=2),
        ),
    ]
