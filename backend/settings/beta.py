from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# PRODUCTION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('BIA_DB_NAME_BT'),
        'USER': os.environ.get('BIA_DB_USER_BT'),
        'PASSWORD': os.environ.get('BIA_DB_PASSWORD_BT'),
        'HOST': os.environ.get('BIA_DB_HOST_BT'),
        'PORT': os.environ.get('BIA_DB_PORT_BT'),
        'ATOMIC_REQUESTS': True
    }
}