from django.template import engines


def render_template(template_string, context):
    # Get the Django template engine
    django_engine = engines['django']
    
    # Create a template object from the template string
    template = django_engine.from_string(template_string)
    
    # Render the template with the provided context
    output = template.render(context)
    
    return output
