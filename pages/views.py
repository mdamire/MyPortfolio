from django.shortcuts import render

from common.utils import render_template, site_context
from .models import HomePageSection


def HomePageView(request):
    s_context = {}

    sections = [
        {
            'body': render_template(section.body, s_context) if section.render_django_template else section.body,
            'navbar_title': section.navbar_title,
        }
        for section in HomePageSection.objects.all()
    ]

    context = site_context(sections=sections, is_homepage=True)
    
    return render(request, 'pages/homepage.html', context)
