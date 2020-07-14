from django.contrib import admin
from .models import SearchTerm


# Register your models here.

class SearchTermAdmin(admin.ModelAdmin):
    list_display = ('user', '__unicode__', 'ip_address', 'search_date', 'tracking_id')
    list_filter = ('ip_address', 'q')
    search_fields = ['tracking_id']
    exclude = ('user',)


admin.site.register(SearchTerm, SearchTermAdmin)
