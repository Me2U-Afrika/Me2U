# Generated by Django 3.1.1 on 2021-01-29 09:59

from django.db import migrations, models
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20210129_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellerprofile',
            name='email',
            field=models.EmailField(help_text='Provide Business email where customers can sendinquries', max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='sellerprofile',
            name='phone',
            field=models.CharField(help_text='This number will be visible to buyers. Start with country code . i.e +250 785011413', max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='sellerprofile',
            name='verification_id',
            field=stdimage.models.StdImageField(blank=True, help_text='Upload your ID/Passport', null=True, upload_to='images/sellerID'),
        ),
    ]
