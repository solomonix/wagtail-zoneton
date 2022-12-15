from .base import *

DEBUG = True

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["zonetonlodge.org", "www.zonetonlodge.org"]

# Needed for the reverse-proxy
# See https://docs.djangoproject.com/en/4.0/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static Files - Use Linode S3
# See https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', get_podman_secret('zoneton_storage_id', ''))
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', get_podman_secret('zoneton_storage_key', ''))
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', get_podman_secret('zoneton_storage_bucket', ''))
AWS_DEFAULT_ACL = 'public-read' 
AWS_CUSTOM_DOMAIN = 'zoneton-web.us-southeast-1.linodeobjects.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_S3_REGION_NAME = 'us-southeast-1'
AWS_S3_ENDPOINT_URL= 'https://' + AWS_S3_REGION_NAME + '.linodeobjects.com'
AWS_S3_USE_SSL=True


# Static files on S3
STATIC_LOCATION = 'static'
STATIC_URL = "https://" + AWS_CUSTOM_DOMAIN + "/" + STATIC_LOCATION + "/"
STATICFILES_STORAGE = 'zoneton_lodge.storage_backends.StaticStorage'

# Public media files on S3
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = "https://" + AWS_CUSTOM_DOMAIN + "/" + PUBLIC_MEDIA_LOCATION + "/"
DEFAULT_FILE_STORAGE = 'zoneton_lodge.storage_backends.PublicMediaStorage'

# Private media files on S3
PRIVATE_MEDIA_LOCATION = 'private'
PRIVATE_FILE_STORAGE = 'zoneton_lodge.storage_backends.PrivateMediaStorage'


try:
    from .local import *
except ImportError:
    pass
