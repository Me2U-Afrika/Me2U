# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-05-22 00:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0005_item_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default='rent a denim at a cheap price for a day'),
            preserve_default=False,
        ),
    ]