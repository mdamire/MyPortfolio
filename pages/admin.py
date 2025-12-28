from django.contrib import admin
from django.db import models
from django.utils import timezone
from tinymce.widgets import TinyMCE
from django.urls import reverse
from django.utils.html import format_html

from common.static import get_css_url_list
from common.models import SiteAsset
from .models import HomePageSection, StaticPage


def publish_page(modeladmin, request, queryset):
    for obj in queryset:
        obj.is_published = True
        obj.save()


@admin.register(HomePageSection)
class HomePageSectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "serial",
        "navbar_title",
    )

    formfield_overrides = {
        models.TextField: {
            "widget": TinyMCE(mce_attrs={"content_css": get_css_url_list()})
        }
    }


class SiteAssetInline(admin.TabularInline):
    model = SiteAsset
    extra = 1
    fields = ("key", "file", "description", "is_active", "is_static")
    fk_name = "page"


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = (
        "permalink",
        "heading",
        "is_published",
        "navbar_title",
        "navbar_serial",
        "created",
        "_url",
    )
    actions = (publish_page,)
    readonly_fields = ("_url",)
    inlines = [SiteAssetInline]

    def _url(self, obj):
        try:
            url = reverse("static-page", kwargs={"permalink": obj.permalink})
            return format_html(f'<a href="{url}" target="_blank">{url}</a>')
        except:
            return

    formfield_overrides = {
        models.TextField: {
            "widget": TinyMCE(
                mce_attrs={"content_css": get_css_url_list(["pages/prism.css"])}
            )
        }
    }
