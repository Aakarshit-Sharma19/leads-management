import dj_database_url
from django.core.management.utils import get_random_secret_key
from os import getenv

# noinspection PyUnresolvedReferences
from leads_management.base_settings import *

SECURE_HSTS_SECONDS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECRET_KEY = getenv('SECRET_KEY', get_random_secret_key())
ALLOWED_HOSTS = getenv('ALLOWED_HOSTS', '').split(',')
DEBUG = False

db_url = getenv('DATABASE_URL')
assert db_url
DATABASES = {
    'default': dj_database_url.parse(db_url, ssl_require=True)
}
