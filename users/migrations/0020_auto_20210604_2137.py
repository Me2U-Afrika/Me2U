# Generated by Django 3.1.1 on 2021-06-04 19:31
from django.db import migrations

def migrate_seller_profile_user_relations(apps, schema_editor):
    SellerProfile = apps.get_model('users', 'SellerProfile')
    # print(SellerProfile)
    Profile = apps.get_model('users', 'Profile')
    # print('profile:', Profile)
    Brand = apps.get_model('me2ushop', 'Brand')
    # print('Brand:', Brand)

    for seller_profile in SellerProfile.objects.all():
        profile = Profile.objects.get_or_create(user=seller_profile.user)
        if profile:
            profile = profile[0]
            print('profile:', profile)
            profile.first_name = seller_profile.first_name
            profile.last_name = seller_profile.last_name
            profile.phone = seller_profile.phone
            profile.save()

            brands = seller_profile.brand_set.all()

            for brand in brands:
                brand.profile = profile
                brand.business_email = seller_profile.email
                brand.business_phone = seller_profile.phone
                brand.application_status = seller_profile.application_status
                brand.user = None
                brand.save()

    SellerProfile.objects.all().delete()




class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20210604_1957'),
    ]

    operations = [
        migrations.RunPython(migrate_seller_profile_user_relations, migrations.RunPython.noop)
    ]


