from django.db import models
from django.conf import settings

from basehome.models import PostBase

# Create your models here.

class ProjectPosts(PostBase):
    body = models.TextField(null=True, blank=True)
    parent = models.ForeignKey(
        "self", 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name="children"
    )
    serial = models.FloatField(null=True, blank=True)

    url_name = "projects:details"

    @property
    def is_parent(self):
        return not self.parent

    @property
    def absolute_url(self):
        return f"{settings.DOMAIN}/projects/{self.url_param}"

    def __str__(self) -> str:
        return self.title
    