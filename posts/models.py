from django.db import models
from model_utils.models import TimeStampedModel

from common.models import AbstractRenderableContent


class PostDetail(TimeStampedModel, AbstractRenderableContent):
    permalink = models.CharField(
        max_length=80, unique=True, 
        help_text="Allowed characters: Need to start with a letter followed by letter, number and underscore"
    )
    heading = models.CharField(max_length=200, help_text="max length: 200")
    introduction = models.TextField()
    is_published = models.BooleanField(default=False)
    publish_date = models.DateField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
