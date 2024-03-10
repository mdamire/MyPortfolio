from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', True)

ALLOWED_HOSTS = os.environ['ALLOWED_HOST'].split(',')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['MYSQL_DATABASE'],
        'USER': os.environ['MYSQL_USER'],
        'PASSWORD': os.environ['MYSQL_PASSWORD'],
        'HOST': os.environ['MYSQL_HOST'],
        'PORT': os.environ['MYSQL_PORT'],
    }
}
