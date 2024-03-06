from django.db import models
from model_utils.models import TimeStampedModel

from common.models import AbstractRenderableContent


class HomePageSection(TimeStampedModel, AbstractRenderableContent):
    name = models.CharField(
        max_length=32, 
        help_text="Enter a descriptive name that helps identify this item in the list."
    )
    navbar_title = models.CharField(
        max_length=128, null=True, blank=True, 
        help_text="Entering a value here will display it's link in the top bar."
    )
    serial = models.IntegerField(default=0)

    class Meta:
        ordering = ('serial', 'created')
