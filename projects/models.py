from django.db import models

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
    body = models.CharField(max_length=7000, null=True, blank=True)
    update_date = models.DateField()
    publish_date = models.DateField()

    def is_child(self):
        if self.parent:
            return True

        return False

    def __str__(self) -> str:
        return self.title
    