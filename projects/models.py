from django.db import models

# Create your models here.

class ProjectPosts(models.Model):
    title = models.CharField(max_length=250)
    url = models.CharField(max_length=40)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    serial = models.FloatField(null=True)
    body = models.CharField(max_length=3500, null=True)
    update_date = models.DateField()
    publish_date = models.DateField()

    def __str__(self) -> str:
        return self.title
    