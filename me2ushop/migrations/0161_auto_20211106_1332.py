# Generated by Django 3.1.1 on 2021-11-06 11:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('me2ushop', '0160_auto_20211028_0253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('P', 'Paypal'), ('S', 'Stripe'), ('M', 'M-Pesa')], max_length=2),
        ),
        migrations.CreateModel(
            name='NameYourPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False, null=True, verbose_name='creation date and time')),
                ('modified', models.DateTimeField(editable=False, null=True, verbose_name='modification date and time')),
                ('suggested_price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('counter_price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('quantity', models.IntegerField()),
                ('accepted', models.BooleanField()),
                ('active', models.BooleanField(default=True)),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='me2ushop.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DiscountTier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False, null=True, verbose_name='creation date and time')),
                ('modified', models.DateTimeField(editable=False, null=True, verbose_name='modification date and time')),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('min_quantity', models.IntegerField(default=1)),
                ('max_quantity', models.IntegerField(blank=True, null=True)),
                ('discount_price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='me2ushop.product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]