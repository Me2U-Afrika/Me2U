# Generated by Django 3.1.1 on 2020-10-17 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_searchterm_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchterm',
            name='category_searched',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
