import re

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from .models import SiteAsset


class SiteAssetForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

    def clean_key(self):
        key = self.cleaned_data['key']
        if not re.match('^[A-Za-z][A-Za-z0-9_]*$', key):
            raise ValidationError("Invalid Value")
        
        return key


@admin.register(SiteAsset)
class SiteAssetAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', '_url')
    form = SiteAssetForm
    readonly_fields = ('_url',)

    def _url(self, obj):
        return format_html(f'<a href="{obj.file.url}" target="_blank">{obj.file.url}</a>')
