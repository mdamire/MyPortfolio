from django.shortcuts import render

from common.static import get_static_context
from common.utils import render_template
from .models import HomePageSection


def HomePageView(request):
    ncontext = {'ctest': 'TEST WORKED'}
    sections = [
        {'body': render_template('{% load static %}' + sec.body, ncontext)}
        for sec in HomePageSection.objects.all()
    ]

    context = {
        'sections': sections,
        'nav_items': [
            {
                'url': '#scrollspyHeading1',
                'title': 'Heading 1'
            },
            {
                'url': '#scrollspyHeading2',
                'title': 'Heading 2'
            },
        ],
        
    }
    context.update(get_static_context())
    
    return render(request, 'pages/homepage.html', context)
