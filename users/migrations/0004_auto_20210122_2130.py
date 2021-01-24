# Generated by Django 3.1.1 on 2021-01-22 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210122_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellerprofile',
            name='email',
            field=models.EmailField(help_text='Provide Business email where customers can send inquries', max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='sellerprofile',
            name='phone',
            field=models.CharField(help_text='This number will be visible to buyers who would like to contact you for services. i.e +250785011413', max_length=20),
        ),
    ]