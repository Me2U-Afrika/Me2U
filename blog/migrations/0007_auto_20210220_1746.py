# Generated by Django 3.1.1 on 2021-02-20 15:46

from django.conf import settings
from django.db import migrations, models
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0006_auto_20210220_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(related_name='post_likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=stdimage.models.StdImageField(blank=True, help_text='upload blog cover Image', null=True, upload_to='images/products'),
        ),
    ]
