import re

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from .models import SiteAsset


class SiteAssetForm(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def clean_key(self):
        key = self.cleaned_data["key"]
        if not re.match("^[A-Za-z][A-Za-z0-9_]*$", key):
            raise ValidationError("Invalid Value")

        return key


@admin.register(SiteAsset)
class SiteAssetAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "post",
        "page",
        "homepage_section",
        "is_active",
        "is_static",
        "description",
        "_url",
    )
    list_filter = ("is_active", "is_static", "post", "page", "homepage_section")
    search_fields = (
        "key",
        "description",
        "post__permalink",
        "post__heading",
        "page__permalink",
        "page__heading",
        "homepage_section__name",
    )
    form = SiteAssetForm
    readonly_fields = ("_url",)

    def _url(self, obj):
        return format_html(
            '<a href="{}" target="_blank">{}</a>', obj.file.url, obj.file.url
        )
