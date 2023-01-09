from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE
from django.utils.html import format_html
from django.conf import settings

from .models import BlogsPosts, BlogsTags


class BlogsPostsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'url_param', 'is_published', 'post_link')
    formfield_overrides = {
        models.TextField : {'widget': TinyMCE()}
    }

    def post_link(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.absolute_url)

# Register your models here.
admin.site.register(BlogsPosts, BlogsPostsAdmin)
admin.site.register(BlogsTags)