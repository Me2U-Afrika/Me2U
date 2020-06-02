# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-05-31 16:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0024_coupon_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuantityCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantityCart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='me2ushop.OrderItem')),
            ],
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='user',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='item',
            name='quantityOrder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='me2ushop.QuantityCart'),
        ),
    ]
