# Generated by Django 3.1.1 on 2021-07-20 23:46

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0122_auto_20210721_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('S', 'Stripe'), ('M', 'M-Pesa'), ('P', 'Paypal')], max_length=2),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=ckeditor.fields.RichTextField(max_length=400),
        ),
    ]