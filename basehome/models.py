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

    def __str__(self):
        return self.title
