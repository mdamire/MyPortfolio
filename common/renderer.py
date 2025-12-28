from django.template import engines

from .models import SiteAsset, AbstractRenderableContent


def render_django_template(template_string, context={}):
    # Get the Django template engine
    django_engine = engines["django"]

    # load dango tags
    template_string = "{% load static %} {% load i18n %}" + template_string

    # Create a template object from the template string
    template = django_engine.from_string(template_string)

    # Render the template with the provided context
    output = template.render(context)

    return output


class ContentRenderer:
    """
    Handles double Django template rendering for content objects.

    First renders the saved content field containing Django template code,
    then passes the rendered content to the actual template for final rendering.
    """

    def get_content_context_data(self, obj, *args, **kwargs):
        """Provides context data for rendering the content field.

        This needs to include any context that would be needed to render the saved content.
        """
        context = {}
        for site_asset in SiteAsset.objects.all():
            context[site_asset.key] = site_asset.file

        return context

    def render_content(self, renderable_object: AbstractRenderableContent):
        if not isinstance(renderable_object, AbstractRenderableContent):
            return renderable_object

        if renderable_object.requires_rendering:
            renderable_object.content = render_django_template(
                renderable_object.content,
                self.get_content_context_data(renderable_object),
            )

        return renderable_object
