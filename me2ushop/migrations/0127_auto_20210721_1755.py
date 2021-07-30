# Generated by Django 3.1.1 on 2021-07-21 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('me2ushop', '0126_auto_20210721_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariation',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='me2ushop.product'),
        ),
        migrations.AlterField(
            model_name='variation',
            name='variation_name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='variation',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='variation',
            name='product',
        ),
    ]