from .base import *

SECRET_KEY = get_secret_value('SECRET_KEY')

DEBUG = bool(get_secret_value('DJANGO_DEBUG', False))

ALLOWED_HOSTS = get_secret_value('ALLOWED_HOST').split(',')

CSRF_TRUSTED_ORIGINS = get_secret_value('CSRF_TRUSTED_ORIGINS').split(',')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_secret_value('DB_NAME'),
        'USER': get_secret_value('DB_USER'),
        'PASSWORD': get_secret_value('DB_PASSWORD'),
        'HOST': get_secret_value('DB_HOST'),
        'PORT': get_secret_value('DB_PORT'),
    }
}
 