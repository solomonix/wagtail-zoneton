from .base import *

DEBUG = False

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {
            "options": "-c search_path=zlschema",
        },
        "NAME": "zoneton_lodge",
        "USER": "zoneton_lodge",
        "PASSWORD": "test123",
        "HOST": "zoneton-postgres",
        "PORT": "",
    }
}

try:
    from .local import *
except ImportError:
    pass
