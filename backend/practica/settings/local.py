import dj_database_url

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'practica.test']
EXTERNAL_URL = ' http://practica.test:4207'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

# URL used in order to authenticate users with an external AD Service, UPT in our case
AUTH_SERVICE_URL = 'https://run.mocky.io/v3/1369cf47-4726-4dbe-867a-88ba1755b008'
AUTH_SERVICE_API_KEY = ''

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

db_path = os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': dj_database_url.parse('sqlite:///' + db_path)
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

PRIVATE_STORAGE_SERVER = 'django'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q!&xztgmpsknc$i5@bu@%sinq5w21l8x4zr9jl&-s(11639sve'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += [
    'django_extensions',
]
