from django.views.generic import ListView, DetailView

from common.mixins import (
    SiteContextMixin,
    MultipleObjectContentRendererMixin,
    SingleObjectContentRendererMixin,
)
from .models import HomePageSection, StaticPage


class HomePageView(ListView, SiteContextMixin, MultipleObjectContentRendererMixin):
    template_name = "pages/homepage.html"
    is_homepage = True
    context_object_name = "sections"
    model = HomePageSection


class StaticPageView(DetailView, SiteContextMixin, SingleObjectContentRendererMixin):
    template_name = "pages/staticpage.html"
    model = StaticPage
    context_object_name = "page"
    slug_field = "permalink"
    slug_url_kwarg = "permalink"

    extra_statics = ["pages/prism.css", "pages/prism.js"]
