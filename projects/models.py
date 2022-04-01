from django.db import models

# Create your models here.

class ProjectPosts(models.Model):
    title = models.CharField(max_length=100)
    sub_title = models.CharField(max_length=500)
    url_name = models.CharField(
            max_length=40, 
            default='details', 
            null=False,
            blank=False,
        )
    url_param = models.CharField(max_length=40, unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    serial = models.FloatField(null=True)
    body = models.CharField(max_length=7000, null=True)
    update_date = models.DateField()
    publish_date = models.DateField()

    def __str__(self) -> str:
        return self.title
    