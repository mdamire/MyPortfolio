# Generated by Django 4.0.2 on 2022-03-30 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_rename_upadte_date_projectposts_update_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectposts',
            old_name='parent_id',
            new_name='parent',
        ),
        migrations.AlterField(
            model_name='projectposts',
            name='serial',
            field=models.FloatField(null=True),
        ),
    ]