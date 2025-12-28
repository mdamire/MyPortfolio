from django.views.generic import ListView, DetailView

from common.mixins import (
    SiteContextMixin,
    MultipleObjectContentRendererMixin,
    SingleObjectContentRendererMixin,
)
from common.models import SiteAsset
from .models import HomePageSection, StaticPage


class HomePageView(ListView, SiteContextMixin, MultipleObjectContentRendererMixin):
    template_name = "pages/homepage.html"
    is_homepage = True
    context_object_name = "sections"
    model = HomePageSection

    def get_extra_statics(self):
        extras = super().get_extra_statics()

        # Add assets for all active homepage sections
        active_sections = HomePageSection.objects.filter(is_active=True)
        for section in active_sections:
            extras.extend(
                [
                    asset.file.url
                    for asset in SiteAsset.objects.filter(
                        homepage_section=section, is_active=True, is_static=True
                    )
                ]
            )
        return extras

    def get_content_context_data(self, obj):
        context = super().get_content_context_data(obj)

        # Add non-static assets for this section as context variables
        for asset in SiteAsset.objects.filter(
            homepage_section=obj, is_active=True, is_static=False
        ):
            context[asset.key] = asset.file

        return context


class StaticPageView(DetailView, SiteContextMixin, SingleObjectContentRendererMixin):
    template_name = "pages/staticpage.html"
    model = StaticPage
    context_object_name = "page"
    slug_field = "permalink"
    slug_url_kwarg = "permalink"

    def get_extra_statics(self):
        extras = super().get_extra_statics()

        # Add Prism syntax highlighting library for code blocks
        extras.extend(["pages/prism.css", "pages/prism.js"])

        # add assets for this page
        extras.extend(
            [
                asset.file.url
                for asset in SiteAsset.objects.filter(
                    page=self.object, is_active=True, is_static=True
                )
            ]
        )
        return extras

    def get_content_context_data(self, obj):
        context = super().get_content_context_data(obj)

        for asset in SiteAsset.objects.filter(
            page=obj, is_active=True, is_static=False
        ):
            context[asset.key] = asset.file

        return context
