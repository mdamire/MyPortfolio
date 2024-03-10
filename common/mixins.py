from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from .navbar import get_navbar_items
from .static import get_static_full_list
from .renderer import ContentRenderer


class SiteContextMixin(ContextMixin):
    is_homepage = False
    extra_statics = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar_items'] = get_navbar_items(self.is_homepage)
        context['statics'] = list(get_static_full_list(self.extra_statics))
        context['is_homepage'] = self.is_homepage

        return context


class SingleObjectContentRendererMixin(SingleObjectMixin, ContentRenderer):

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj = self.render_content(obj)

        return obj


class MultipleObjectContentRendererMixin(MultipleObjectMixin, ContentRenderer):

    def get_queryset(self):
        qs = super().get_queryset()

        for obj in qs:
            obj = self.render_content(obj)
        
        return qs
