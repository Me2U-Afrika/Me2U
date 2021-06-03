from django.db import migrations, models

def populate_profile(apps, schema_editor):
    SellerProfile = apps.get_model("")