# Generated by Django 3.1.1 on 2021-07-20 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0016_faq'),
    ]

    operations = [
        migrations.AddField(
            model_name='faq',
            name='category',
            field=models.CharField(blank=True, choices=[('General', 'General'), ('Orders', 'Orders'), ('Payment', 'Payment'), ('Seller', 'Seller')], max_length=10, null=True),
        ),
    ]