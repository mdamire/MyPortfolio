from django.contrib import admin

from .models import BlogsPosts, BlogsTags

# Register your models here.
admin.site.register(BlogsPosts)
admin.site.register(BlogsTags)