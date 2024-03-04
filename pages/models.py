from django.db import models
from model_utils.models import TimeStampedModel


class HomePageSection(TimeStampedModel):
    name = models.CharField(
        max_length=32, 
        help_text="Enter a descriptive name that helps identify this item in the list."
    )
    body = models.TextField()
    navbar_title = models.CharField(
        max_length=128, null=True, blank=True, 
        help_text="Entering a value here will display it's link in the top bar."
    )
    serial = models.IntegerField(default=0)
    render_django_template = models.BooleanField(
        default=False, 
        help_text="Set this to true, when the 'body' field contains Django template code that requires rendering"
    )

    class Meta:
        ordering = ('serial', 'created')
