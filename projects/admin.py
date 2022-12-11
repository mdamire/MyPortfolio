from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

from .models import ProjectPosts

class ProjectPostsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'url_param', 'is_published')
    formfield_overrides = {
        models.TextField : {'widget': TinyMCE()}
    }

# Register your models here.
admin.site.register(ProjectPosts, ProjectPostsAdmin)