# Generated by Django 4.0.2 on 2022-04-01 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0002_remove_blogsposts_tags_delete_blogstags'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogsTags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
            ],
        ),
    ]