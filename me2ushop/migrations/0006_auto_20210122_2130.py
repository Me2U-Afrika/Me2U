# Generated by Django 3.1.1 on 2021-01-22 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210122_2130'),
        ('me2ushop', '0005_auto_20210122_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('P', 'Paypal'), ('D', 'Debit Card'), ('S', 'Stripe'), ('C', 'Cash On Delivery'), ('M', 'M-Pesa')], max_length=2),
        ),
        migrations.AlterField(
            model_name='brand',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.sellerprofile'),
        ),
        migrations.AlterField(
            model_name='product',
            name='condition',
            field=models.CharField(choices=[('C', 'Certified'), ('N', 'New'), ('U', 'Used'), ('R', 'Refurbished')], help_text='Choose the current condition for the product', max_length=2),
        ),
    ]
