# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-05-29 05:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0013_auto_20200529_0240'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]