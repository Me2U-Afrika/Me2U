# Generated by Django 3.1.1 on 2021-07-20 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0019_auto_20210720_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='faq',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='marketing.faqcategory'),
        ),
    ]
