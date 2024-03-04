# Generated by Django 4.0.2 on 2024-03-01 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='The asset will be made available using this key as a context nameOnly use one word or multiple words with underscore.\nAllowed letters: \n  * Uppercase Letters\n  * Lowercase Letters\n  * Numbers (cannot be the first digit)\n  * Underscore\nMax length: 128 characters', max_length=128)),
                ('file', models.FileField(help_text='You can use this using the full url which can be found after saving the data.\nOr this will be available for your homepage sections or posts as context variable where \nkey is the name of the context variable', upload_to='assets/')),
                ('description', models.TextField(blank=True, help_text='A note to yourself of where or how this can be used', null=True)),
            ],
        ),
    ]