# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-06-03 11:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0033_requestrefund_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestrefund',
            name='ref_code',
            field=models.CharField(default='herewerputcode', max_length=20),
            preserve_default=False,
        ),
    ]