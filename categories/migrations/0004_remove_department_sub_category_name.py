# Generated by Django 3.1.1 on 2021-02-03 21:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_department_sub_category_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='sub_category_name',
        ),
    ]
