from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE
from django.urls import reverse
from django.utils.html import format_html

from common.static import get_css_full_list
from .models import HomePageSection, StaticPage


@admin.register(HomePageSection)
class HomePageSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial', 'navbar_title',)

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(mce_attrs={'content_css': get_css_full_list()})}
    }

@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('permalink', 'heading', 'is_published', 'navbar_title', 'navbar_serial', 'created', '_url')

    def _url(self, obj):
        url = reverse('static-page', kwargs={'permalink': obj.permalink})
        return format_html(f'<a href="{url}" target="_blank">{url}</a>')
    
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(mce_attrs={'content_css': get_css_full_list()})}
    }
