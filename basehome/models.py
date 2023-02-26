from django.db import models

# Create your models here.
class Image(models.Model):
    title = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

class Files(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='files/')
    key = models.CharField(max_length=100, null=True, unique=True)

    def __str__(self):
        return self.title

class PostBase(models.Model):
    title = models.CharField(max_length=100)
    sub_title = models.CharField(max_length=500)
    url_param = models.CharField(max_length=80, unique=True)
    body = models.TextField()
    is_published = models.BooleanField(default=True)
    update_date = models.DateField(auto_now=True)
    publish_date = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True
