from urllib.parse import urlparse

import dj_database_url
import sentry_sdk
from str2bool import str2bool

from .base import *  # noqa: F403


def getenv_assert(key):
    result = os.getenv(key, None)
    assert result, f'the {key} environment variable must be set'
    return result


DEBUG = str2bool(os.getenv('DJANGO_DEBUG', False))

EXTERNAL_URL = getenv_assert('EXTERNAL_URL')
ALLOWED_HOSTS = ['backend', urlparse(EXTERNAL_URL).hostname]

# URL used in order to authenticate users with an external AD Service, UPT in our case
AUTH_SERVICE_URL = getenv_assert('AUTH_SERVICE_URL')
AUTH_SERVICE_API_KEY = getenv_assert('AUTH_SERVICE_API_KEY')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv_assert('DJANGO_SECRET_KEY')

SESSION_COOKIE_SECURE = urlparse(EXTERNAL_URL).scheme == 'https'
CSRF_COOKIE_SECURE = urlparse(EXTERNAL_URL).scheme == 'https'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = urlparse(EXTERNAL_URL).scheme

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')

PRIVATE_STORAGE_INTERNAL_URL = '/private-files/'
PRIVATE_STORAGE_NGINX_VERSION = '1.12.2'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'session'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = getenv_assert('SMTP_USERNAME')
EMAIL_HOST_PASSWORD = getenv_assert('SMTP_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = getenv_assert('SMTP_FROM_EMAIL')
EMAIL_SUBJECT_PREFIX = ""


SILENCED_SYSTEM_CHECKS = [
    'security.W004',  # SECURE_HSTS_SECONDS
    'security.W008',  # SECURE_SSL_REDIRECT
]

# https://sentry.io/liga-ac/practica-backend/
INSTALLED_APPS.append('raven.contrib.django.raven_compat')

SENTRY_DSN = os.getenv('SENTRY_DSN', None)
SENTRY_RELEASE = os.getenv('SENTRY_RELEASE', None)


RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': SENTRY_RELEASE,
    'environment': urlparse(EXTERNAL_URL).hostname,
}

sentry_sdk.init(
    dsn= SENTRY_DSN,
    traces_sample_rate=0.5,
)