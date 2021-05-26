# Generated by Django 3.1.1 on 2021-05-25 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0089_auto_20210525_0049'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='shipping_status',
            field=models.CharField(blank=True, choices=[('Cd', 'Can Ship Abroad and Deliver Locally'), ('Cl', 'Can Deliver Locally'), ('CO', 'Not Able to Deliver')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('P', 'Paypal'), ('M', 'M-Pesa'), ('S', 'Stripe')], max_length=2),
        ),
    ]
