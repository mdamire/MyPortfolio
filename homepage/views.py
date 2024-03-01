from django.shortcuts import render

from .models import HomePageSection
from django.template import engines

def render_template(template_string, context):
    # Get the Django template engine
    django_engine = engines['django']
    
    # Create a template object from the template string
    template = django_engine.from_string(template_string)
    
    # Render the template with the provided context
    output = template.render(context)
    
    return output


# Create your views here.
def HomePageView(request):
    ncontext = {'ctest': 'TEST WORKED'}
    sections = [
        {'body': render_template(sec.body, ncontext)}
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
    return render(request, 'home-page.html', context)