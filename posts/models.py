from django.db import models
from model_utils.models import TimeStampedModel

from common.models import AbstractRenderableContent, SiteAsset


class PostDetail(TimeStampedModel, AbstractRenderableContent):
    permalink = models.CharField(
        max_length=80,
        unique=True,
        help_text="Allowed characters: Need to start with a letter followed by letter, number and underscore",
    )
    heading = models.CharField(max_length=200, help_text="max length: 200")
    introduction = models.TextField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    publish_date = models.DateField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
    include_sublinks = models.BooleanField(
        default=True,
        help_text="Post sublinks will be generated from any header tag and will aprear in Post Content section",
    )
    tags = models.ManyToManyField("PostTag", blank=True)
    feature = models.IntegerField(
        default=0,
        help_text="This value will help it sort in the post list page. Higher value has more priority.",
    )

    @property
    def intro_len(self):
        return len(self.heading) + len(self.introduction)

    def __str__(self) -> str:
        return f"{self.permalink}: {self.heading}"

    class Meta:
        ordering = ["-feature", "-publish_date", "-created"]


class PostTag(TimeStampedModel):
    label = models.CharField(max_length=64)
    color = models.CharField(
        max_length=20,
        default="white",
        help_text="css color (hex, rgb or color name) for text color",
    )
    bg_color = models.CharField(
        max_length=20,
        default="grey",
        help_text="css color (hex, rgb or color name) for background color",
    )

    def __str__(self):
        return self.label

    class Meta:
        ordering = ["-created"]


class PostAsset(TimeStampedModel):
    asset = models.OneToOneField(SiteAsset, on_delete=models.CASCADE)
    post = models.ForeignKey(PostDetail, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created"]
