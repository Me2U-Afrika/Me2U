# Generated by Django 3.1.1 on 2020-12-15 10:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('me2ushop', '0001_initial'),
        ('categories', '0001_initial'),
        ('stats', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stripepayment',
            name='cart_id',
            field=models.ForeignKey(blank=True, max_length=70, null=True, on_delete=django.db.models.deletion.CASCADE, to='stats.productview'),
        ),
        migrations.AddField(
            model_name='stripepayment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='requestrefund',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='me2ushop.order'),
        ),
        migrations.AddField(
            model_name='productreview',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='me2ushop.product'),
        ),
        migrations.AddField(
            model_name='productreview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='productimage',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='me2ushop.product'),
        ),
        migrations.AddField(
            model_name='productdetail',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='me2ushop.productattribute'),
        ),
        migrations.AddField(
            model_name='productdetail',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Details', to='me2ushop.product'),
        ),
        migrations.AddField(
            model_name='product',
            name='brand_name',
            field=models.ForeignKey(blank=True, help_text='Your store name', null=True, on_delete=django.db.models.deletion.SET_NULL, to='me2ushop.brand'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_categories',
            field=models.ManyToManyField(help_text='input the subcategory.', to='categories.Department'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='customer_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='me2ushop.order'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='delivered_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dispatcher', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='me2ushop.product'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='status_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='me2ushop.statuscode'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='me2ushop.coupon'),
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(to='me2ushop.OrderItem'),
        ),
        migrations.AddField(
            model_name='order',
            name='last_spoken_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cs_chats', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='status_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='me2ushop.statuscode'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='brand',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]