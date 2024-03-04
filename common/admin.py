import re
import os
from django.contrib import admin
from .models import SiteAsset
from django import forms
from django.core.exceptions import ValidationError


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
    list_display = ('key', 'description')
    form = SiteAssetForm
