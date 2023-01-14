import logging
import os
from os import getenv

import dj_database_url
from django.core.management.utils import get_random_secret_key

# noinspection PyUnresolvedReferences
from leads_management.base_settings import *

SECRET_KEY = getenv('SECRET_KEY', get_random_secret_key())

SECURE_HSTS_SECONDS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True

ALLOWED_HOSTS = getenv('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
assert len(ALLOWED_HOSTS) > 0 and len(CSRF_TRUSTED_ORIGINS) > 0

DEBUG = False
if os.getenv('ENABLE_DEBUG'):
    DEBUG = True

db_url = getenv('DATABASE_URL')
if db_url:
    DATABASES = {
        'default': dj_database_url.parse(db_url, ssl_require=False)
    }
else:
    logging.warning('DATABASE_URL not defined')
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
