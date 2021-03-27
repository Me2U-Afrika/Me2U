from django.contrib import admin
from .models import *


# Register your models here.

class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content')


class PostAdmin(admin.ModelAdmin):
    list_display = ('product', 'author', 'title')


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, PostCommentAdmin)

