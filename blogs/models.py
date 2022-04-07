from django.db import models

# Create your models here.
class BlogsTags(models.Model):
    name = models.CharField(max_length=80)
    value = models.IntegerField(default=1, null=False, blank=False)

    def __str__(self):
        return self.name

class BlogsPosts(models.Model):
    title = models.CharField(max_length=100)
    sub_title = models.CharField(max_length=500)
    url_param = models.CharField(max_length=80, unique=True)
    tags = models.ManyToManyField(BlogsTags)
    body = models.TextField()
    is_published = models.BooleanField(default=True)
    update_date = models.DateField()
    publish_date = models.DateField()

    def __str__(self) -> str:
        return self.title
