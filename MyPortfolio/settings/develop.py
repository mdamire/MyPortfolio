from .base import *

SITE_URL = "http://localhost:8000"

# Use MySQL if environment variables are set, otherwise fall back to SQLite
DB_NAME = get_secret_value("DB_NAME", None)

if DB_NAME:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": DB_NAME,
            "USER": get_secret_value("DB_USER", "root"),
            "PASSWORD": get_secret_value("DB_PASSWORD", ""),
            "HOST": get_secret_value("DB_HOST", "localhost"),
            "PORT": get_secret_value("DB_PORT", "3306"),
        }
    }
