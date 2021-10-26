# Generated by Django 3.1.1 on 2021-10-18 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0154_auto_20211018_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='contact_person',
            field=models.CharField(blank=True, help_text='Contact person name who will receive inquiries', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('M', 'M-Pesa'), ('P', 'Paypal'), ('S', 'Stripe')], max_length=2),
        ),
    ]