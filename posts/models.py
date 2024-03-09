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
    include_sublinks = models.BooleanField(
        default=True, 
        help_text="Post sublinks will be generated from any header tag and will aprear in Post Content section"
    )

    @property
    def intro_len(self):
        return len(self.heading) + len(self.introduction)
