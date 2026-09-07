# fairhire/settings/development.py
# ─────────────────────────────────────────────────────────────────
#  Development settings — used when running locally with manage.py
# ─────────────────────────────────────────────────────────────────

from .base import *
from decouple import config
import dj_database_url

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    'recruitiq-backend-production-1bcf.up.railway.app',
    'recruitiq-backend-production-4b25.up.railway.app',
    'localhost',
    '127.0.0.1',
]

DATABASE_URL = config('DATABASE_URL', default='', cast=str)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # ── MySQL Database ────────────────────────────
    # Make sure MySQL is installed and running.
    # Create database first:
    #   mysql -u root -p
    #   CREATE DATABASE fairhire_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.mysql',
            'NAME':     config('DB_NAME',     default='fairhire_db'),
            'USER':     config('DB_USER',     default='root'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST':     config('DB_HOST',     default='localhost'),
            'PORT':     config('DB_PORT',     default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# ── Email (console backend for dev) ──────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
