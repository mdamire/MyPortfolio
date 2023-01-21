from django.db import models
from django.conf import settings

from basehome.models import PostBase

# Create your models here.
class BlogsTags(models.Model):
    name = models.CharField(max_length=80)
    value = models.IntegerField(default=1, null=False, blank=False)

    def __str__(self):
        return self.name

class BlogsPosts(PostBase):
    tags = models.ManyToManyField(BlogsTags)

    url_name = 'blogs:details'

    @property
    def absolute_url(self):
        return f"{settings.DOMAIN}/blogs/{self.url_param}"

    def __str__(self) -> str:
        return self.title
