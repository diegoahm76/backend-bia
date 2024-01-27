from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# PRODUCTION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('BIA_DB_NAME_PR'),
        'USER': os.environ.get('BIA_DB_USER_PR'),
        'PASSWORD': os.environ.get('BIA_DB_PASSWORD_PR'),
        'HOST': os.environ.get('BIA_DB_HOST_PR'),
        'PORT': os.environ.get('BIA_DB_PORT_PR'),
        'ATOMIC_REQUESTS': True
    }
}