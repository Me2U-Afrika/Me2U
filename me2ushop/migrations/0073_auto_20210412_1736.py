# Generated by Django 3.1.1 on 2021-04-12 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tagging', '0003_adapt_max_tag_length'),
        ('me2ushop', '0072_auto_20210412_1724'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertagtracker',
            name='tagname',
        ),
        migrations.AddField(
            model_name='usertagtracker',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tagging.tag'),
        ),
        migrations.AlterField(
            model_name='address',
            name='payment_option',
            field=models.CharField(choices=[('D', 'Debit Card'), ('P', 'Paypal'), ('S', 'Stripe'), ('C', 'Cash On Delivery'), ('M', 'M-Pesa')], max_length=2),
        ),
        migrations.AlterField(
            model_name='product',
            name='condition',
            field=models.CharField(choices=[('N', 'New'), ('R', 'Refurbished'), ('U', 'Used')], help_text='Choose the current condition for the product', max_length=2),
        ),
    ]