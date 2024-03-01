from django.db import models
from model_utils.models import TimeStampedModel

# Create your models here.
class HomePageSection(TimeStampedModel):
    navbar_title = models.CharField(max_length=128)
    heading = models.CharField(max_length=512)
    body = models.TextField()
    serial = models.IntegerField(default=0)

    class Meta:
        ordering = ('serial', 'created')
