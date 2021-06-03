from django.contrib import admin
from .models import *


# Register your models here.
class MarketingMessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'end_date', 'active']


class SliderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'end_date', 'active']


class MarketingEmailsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created', 'modified']


class BannerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'end_date', 'is_deal', 'active', 'created', 'modified']


class TrendAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created', 'modified']


class TrendInfoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created', 'modified']


class DealsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_featured', 'created', 'modified']
    list_editable = ('is_featured',)


class SliderImagesAdmin(admin.ModelAdmin):
    list_display = ['slider']


admin.site.register(MarketingMessage, MarketingMessageAdmin)
admin.site.register(Slider, SliderAdmin)
admin.site.register(MarketingEmails, MarketingEmailsAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Trend, TrendAdmin)
admin.site.register(TrendInfo, TrendInfoAdmin)
admin.site.register(SliderImages, SliderImagesAdmin)
