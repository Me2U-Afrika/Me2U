# Generated by Django 3.1.1 on 2021-04-11 19:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0009_auto_20210411_2126'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'ordering': ['-end_date']},
        ),
    ]
