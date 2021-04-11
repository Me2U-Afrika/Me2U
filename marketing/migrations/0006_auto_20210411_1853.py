# Generated by Django 3.1.1 on 2021-04-11 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0005_auto_20210125_0600'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'ordering': ['-end_date']},
        ),
        migrations.AlterModelOptions(
            name='marketingmessage',
            options={'ordering': ['-end_date']},
        ),
        migrations.AlterModelOptions(
            name='slider',
            options={'ordering': ['-end_date']},
        ),
        migrations.AlterModelOptions(
            name='trend',
            options={'ordering': ['end_date']},
        ),
        migrations.RemoveField(
            model_name='banner',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='slider',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='trend',
            name='start_date',
        ),
        migrations.AlterField(
            model_name='banner',
            name='active',
            field=models.BooleanField(default=True, editable=False),
        ),
    ]
