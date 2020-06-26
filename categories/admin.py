from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'description', 'is_active', 'created_at', 'updated_at',)
    list_display_links = ('category_name',)
    list_per_page = 20
    ordering = ['category_name']
    search_fields = ['name', 'description', 'meta_keywords', 'meta_description']
    exclude = ('created_at',
               'updated_at',)
    # sets up slug to be generated from category name
    prepopulated_fields = {'slug': ('category_name',)}


admin.site.register(Category, CategoryAdmin)

