import os
from typing import Any, Dict
from itertools import chain
from operator import attrgetter

from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings

from projects.models import ProjectPosts
from blogs.models import BlogsPosts
from .api import get_file_from_key


class HomeView(TemplateView):
    template_name = 'contents/home.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        projects = ProjectPosts.objects.order_by('-publish_date').filter(parent__isnull=True, is_published=True)
        blogs = BlogsPosts.objects.order_by('-publish_date').filter(is_published=True)

        post_list = sorted(
            chain(projects, blogs), 
            key=attrgetter('publish_date'),
            reverse=True
        )[:5]
        context['post_list'] = post_list

        context['my_email'] = settings.MY_EMAIL
        return context


class AboutView(TemplateView):
    template_name = 'contents/about.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['my_email'] = settings.MY_EMAIL
        context['cv'] = get_file_from_key(settings.CV_FILE)
        return context
