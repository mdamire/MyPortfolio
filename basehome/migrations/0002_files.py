# Generated by Django 4.0.2 on 2022-04-21 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basehome', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='files/')),
            ],
        ),
    ]
