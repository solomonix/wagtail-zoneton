from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-8n*q)u$j#iuq-ia6^_2x64voi^v6sfli1xpz+my@-ycjrfz*61"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
#        "OPTIONS": {
#            "options": "-c search_path=zlschema",
#        },
        "NAME": "zoneton_lodge",
        "USER": "zoneton_lodge",
        "PASSWORD": "test123",
        "HOST": "db",
        "PORT": "5432",
    }
}

try:
    from .local import *
except ImportError:
    pass
