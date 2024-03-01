from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE
from .models import HomePageSection

# Register your models here.
@admin.register(HomePageSection)
class HomePageSectionAdmin(admin.ModelAdmin):
    list_display = ('serial', 'navbar_title', 'heading')

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE}
    }
