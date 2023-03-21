import logging

logger = logging.getLogger('settings')
from os import getenv

import dj_database_url

# noinspection PyUnresolvedReferences
from leads_management.settings.base_settings import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-%va6o!*&(ac-=*$6o5^j^%gh^8he=w35s8+^5tc4e(+43+4my-"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

db_url = getenv('DATABASE_URL')
if db_url:
    DATABASES = {
        'default': dj_database_url.parse(db_url, ssl_require=False)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
