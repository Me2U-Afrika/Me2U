# Generated by Django 3.1.1 on 2021-07-30 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0133_auto_20210727_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('S', 'Stripe'), ('M', 'M-Pesa'), ('P', 'Paypal')], max_length=2),
        ),
        migrations.AlterField(
            model_name='brand',
            name='title',
            field=models.CharField(help_text='Unique business title to identify Your store and your product line', max_length=200, unique=True),
        ),
    ]
