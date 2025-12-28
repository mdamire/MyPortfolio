from django.db import models
from model_utils.models import TimeStampedModel

from common.models import AbstractRenderableContent, AbstractAsset


class HomePageSection(TimeStampedModel, AbstractRenderableContent):
    name = models.CharField(
        max_length=32,
        help_text="Enter a descriptive name that helps identify this item in the list.",
    )
    navbar_title = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="Entering a value here will display it's link in the top bar.",
    )
    serial = models.IntegerField(default=0)

    class Meta:
        ordering = ("serial", "created")


class StaticPage(TimeStampedModel, AbstractRenderableContent):
    permalink = models.CharField(
        max_length=80,
        unique=True,
        help_text="Allowed characters: Need to start with a letter followed by letter, number and underscore",
    )
    heading = models.CharField(max_length=200, help_text="max length: 200")
    is_published = models.BooleanField(default=False)
    navbar_title = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text="When populated, this field will display the specified title on the navbar before 'POSTS'.",
    )
    navbar_serial = models.IntegerField(
        default=0, help_text="Not effective if no navbar_title"
    )

    def __str__(self) -> str:
        return f"{self.permalink}: {self.heading}"


class PageAsset(TimeStampedModel, AbstractAsset):
    page = models.ForeignKey(
        StaticPage, on_delete=models.CASCADE, null=True, blank=True,
        help_text="Associated page for this asset. If left blank, the asset is considered home page asset."
    )

    class Meta:
        ordering = ["-created"]
