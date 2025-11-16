from django.conf import settings
import os


def get_full_url(url):
    if not url:
        return None

    # If already an absolute URL, return as is
    if url.startswith(("http://", "https://")):
        return url

    site_url = settings.SITE_URL.rstrip("/")
    url = url.lstrip("/")

    return f"{site_url}/{url}"
