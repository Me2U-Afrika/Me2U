# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-06-01 03:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0027_item_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quantitycart',
            name='quantityCart',
        ),
        migrations.RemoveField(
            model_name='item',
            name='quantity',
        ),
        migrations.AddField(
            model_name='order',
            name='being_delivered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='received',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund_granted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='QuantityCart',
        ),
    ]
