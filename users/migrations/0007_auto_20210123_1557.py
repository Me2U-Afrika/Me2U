# Generated by Django 3.1.1 on 2021-01-23 13:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20210123_0615'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sellerprofile',
            old_name='tax_country',
            new_name='country',
        ),
    ]
