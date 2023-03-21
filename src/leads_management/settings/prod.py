from os import getenv

# noinspection PyUnresolvedReferences
from leads_management.settings.base_settings import *
from leads_management.settings.secrets_utils import DB_CREDENTIALS

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

DEBUG = bool(os.getenv('ENABLE_DEBUG'))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'leads_management_database'),
        'USER': DB_CREDENTIALS['username'],
        'PASSWORD': DB_CREDENTIALS['password'],
        'HOST': getenv('DB_HOST'),
        'PORT': getenv('DB_PORT', '5432'),
    }
}