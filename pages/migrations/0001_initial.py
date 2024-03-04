# Generated by Django 4.0.2 on 2024-03-04 02:13

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HomePageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(help_text='Enter a descriptive name that helps identify this item in the list.', max_length=32)),
                ('body', models.TextField()),
                ('navbar_title', models.CharField(blank=True, help_text="Entering a value here will display it's link in the top bar.", max_length=128, null=True)),
                ('serial', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('serial', 'created'),
            },
        ),
    ]
