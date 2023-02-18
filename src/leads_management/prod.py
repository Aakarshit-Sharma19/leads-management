import dj_database_url
from os import getenv

# noinspection PyUnresolvedReferences
from leads_management.base_settings import *

logger = logging.getLogger('settings')

SECRET_KEY = getenv('SECRET_KEY')
if not SECRET_KEY:
    logger.error("Fatal Error: SECRET_KEY not defined.")
    raise AssertionError

SECURE_HSTS_SECONDS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True

ALLOWED_HOSTS = getenv('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
assert len(ALLOWED_HOSTS) > 0 and len(CSRF_TRUSTED_ORIGINS) > 0
logger.warning(f'ALLOWED_HOSTS: {ALLOWED_HOSTS}')
logger.warning(f'CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}')

# Allauth
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

DEBUG = False
if os.getenv('ENABLE_DEBUG'):
    DEBUG = True

db_url = getenv('DATABASE_URL')
if db_url:
    DATABASES = {
        'default': dj_database_url.parse(db_url, ssl_require=False)
    }
else:
    logger.error('Fatal Error: DATABASE_URL not defined.')
    raise AssertionError
