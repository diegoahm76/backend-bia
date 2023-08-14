from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# LOCAL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': os.environ.get('BIA_DB_USER'),
        'PASSWORD': 'NYRRXW0WR30oW35p09U2',
        'HOST': 'containers-us-west-126.railway.app',
        'PORT': '5826',
        'ATOMIC_REQUESTS': True
    },
    'bia-estaciones': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('BIA_ESTACIONES_NAME'),
        'USER': os.environ.get('BIA_ESTACIONES_USER'),
        'PASSWORD': os.environ.get('BIA_ESTACIONES_PASSWORD'),
        'HOST': os.environ.get('BIA_ESTACIONES_HOST'),
        'PORT': os.environ.get('BIA_ESTACIONES_PORT'),
        'ATOMIC_REQUESTS': True
    }
}