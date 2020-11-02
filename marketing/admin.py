from django.contrib import admin
from .models import MarketingMessage, Slider, MarketingEmails, Banner, Deals


# Register your models here.
class MarketingMessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'start_date', 'end_date', 'active']


class SliderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'start_date', 'end_date', 'active']


class MarketingEmailsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created', 'modified']


class BannerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created', 'modified']


class DealsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created', 'modified']


admin.site.register(MarketingMessage, MarketingMessageAdmin)
admin.site.register(Slider, SliderAdmin)
admin.site.register(MarketingEmails, MarketingEmailsAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Deals, DealsAdmin)
