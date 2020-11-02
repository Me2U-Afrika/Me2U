# Generated by Django 3.1.1 on 2020-10-14 13:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('me2ushop', '0024_auto_20201013_0318'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productimage',
            options={'ordering': ('-created',)},
        ),
        migrations.RemoveField(
            model_name='product',
            name='brand',
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('M', 'M-Pesa'), ('P', 'Paypal'), ('D', 'Debit Card'), ('S', 'Stripe'), ('C', 'Cash On Delivery')], max_length=2),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False, verbose_name='creation date and time')),
                ('modified', models.DateTimeField(editable=False, null=True, verbose_name='modification date and time')),
                ('title', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='product',
            name='brand_name',
            field=models.ForeignKey(blank=True, help_text='Your store name', null=True, on_delete=django.db.models.deletion.SET_NULL, to='me2ushop.brand'),
        ),
    ]
