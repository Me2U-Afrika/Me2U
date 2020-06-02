from django.contrib import admin
from .models import Addicts


class AddictsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'age', 'location', 'availability')


class ReferralsAdmin(admin.ModelAdmin):
    list_display = ('description', 'discount')


admin.site.register(Addicts, AddictsAdmin)
# admin.site.register(Referrals, ReferralsAdmin)
# admin.site.register(ads)
# admin.site.register(tags)
