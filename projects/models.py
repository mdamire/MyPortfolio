from django.db import models
from django.conf import settings

# Create your models here.

class ProjectPosts(models.Model):
    title = models.CharField(max_length=100)
    sub_title = models.CharField(max_length=500)
    url_name = models.CharField(
            max_length=40, 
            default='projects:details', 
            null=False,
            blank=False,
        )
    url_param = models.CharField(max_length=40, unique=True)
    is_parent = models.BooleanField(default=False)
    parent = models.ForeignKey(
            "self", 
            on_delete=models.CASCADE, 
            null=True, 
            blank=True,
        )
    serial = models.FloatField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    update_date = models.DateField(auto_now=True)
    publish_date = models.DateField(auto_now_add=True)

    def is_child(self):
        if self.parent:
            return True

        return False

    @property
    def absolute_url(self):
        return f"{settings.DOMAIN}/projects/{self.url_param}"

    def __str__(self) -> str:
        return self.title
    