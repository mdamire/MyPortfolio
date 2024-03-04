from django.template import engines

from .static import get_static_context
from .navbar import get_navbar_context
from .models import SiteAsset


def site_asset_context():
    sac = {}
    for sa in SiteAsset.objects.all():
        sac[sa.key] = sa.file
    
    return sac


def render_template(template_string, extra_context={}):
    # Get the Django template engine
    django_engine = engines['django']

    # Get template context
    context = {}
    context.update(site_asset_context())
    context.update(extra_context)
    
    # load dango tags
    template_string = '{% load static %} {% load i18n %}' + template_string

    # Create a template object from the template string
    template = django_engine.from_string(template_string)
    
    # Render the template with the provided context
    output = template.render(context)
    
    return output


def site_context(is_homepage=False, **kwargs) -> dict:
    context = kwargs
    context.update(get_static_context())
    context.update(get_navbar_context(is_homepage))

    return context
