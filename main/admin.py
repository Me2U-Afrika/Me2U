from django.contrib import admin
from .models import *


class MaDrivers(admin.ModelAdmin):
    list_display = ('name', 'location', 'availability', 'description')


class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
#
#
# class basket(admin.ModelAdmin):
#     list_display = ('user', 'status')


# class ReferralsAdmin(admin.ModelAdmin):
#     list_display = ('description', 'discount')


# admin.site.register(MaDere, MaDrivers)
admin.site.register(ContactUs, ContactUsAdmin)
# admin.site.register(BasketLine, basketline)

# admin.site.register(Referrals, ReferralsAdmin)
# admin.site.register(ads)
# admin.site.register(templatetags)
