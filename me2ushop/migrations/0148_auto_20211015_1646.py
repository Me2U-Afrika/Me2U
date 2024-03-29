# Generated by Django 3.1.1 on 2021-10-15 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0147_auto_20211007_0853'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='shipping_status',
            field=models.CharField(blank=True, choices=[('Cd', 'Can Ship Abroad and Deliver Locally'), ('Cl', 'Can Deliver Locally'), ('CO', 'Not Able to Deliver')], help_text='Is Your company able to ship or deliver your products once they buyers order online?', max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('S', 'Stripe'), ('P', 'Paypal'), ('M', 'M-Pesa')], max_length=2),
        ),
    ]
