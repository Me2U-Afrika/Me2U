# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-06-01 03:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0029_auto_20200601_0528'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]