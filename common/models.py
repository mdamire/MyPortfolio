import re
from django.db import models
from django.core.exceptions import ValidationError


class SiteAsset(models.Model):
    key = models.CharField(
        max_length=128,
        help_text=(
            "The asset will be made available using this key as a context name. "
            "Only use one word or multiple words with underscore. "
            "Allowed letters: * Uppercase Letters * Lowercase Letters "
            "* Numbers (cannot be the first digit)  * Underscore. "
            "Max length: 128 characters."
        ),
    )
    file = models.FileField(
        upload_to="assets/",
        help_text=(
            "You can use this using the full url which can be found after saving the data. "
            "This also will be available for your homepage sections or posts as context variable where "
            "key is the name of the context variable."
        ),
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional: A note to yourself of where or how this can be used.",
    )


class AbstractRenderableContent(models.Model):
    content = models.TextField()
    requires_rendering = models.BooleanField(
        default=False,
        help_text="Set this to true, when the 'content' field contains Django template code that requires rendering",
    )

    class Meta:
        abstract = True
