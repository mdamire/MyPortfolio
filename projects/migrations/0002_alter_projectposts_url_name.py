# Generated by Django 4.0.2 on 2022-04-01 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectposts',
            name='url_name',
            field=models.CharField(default='projects:details', max_length=40),
        ),
    ]