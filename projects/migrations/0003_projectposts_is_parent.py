# Generated by Django 4.0.2 on 2022-04-01 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_alter_projectposts_url_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectposts',
            name='is_parent',
            field=models.BooleanField(default=False),
        ),
    ]
