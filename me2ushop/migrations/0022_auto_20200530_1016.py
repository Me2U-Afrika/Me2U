# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-05-30 08:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0021_auto_20200530_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='code',
            field=models.CharField(max_length=10),
        ),
    ]
