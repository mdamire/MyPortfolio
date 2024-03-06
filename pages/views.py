from django.shortcuts import render
from django.views.generic import ListView

from common.mixins import SiteContextMixin, MultipleObjectContentRendererMixin
from .models import HomePageSection


class HomePageView(ListView, SiteContextMixin, MultipleObjectContentRendererMixin):
    template_name = 'pages/homepage.html'
    is_homepage = True
    context_object_name = 'sections'
    model = HomePageSection
