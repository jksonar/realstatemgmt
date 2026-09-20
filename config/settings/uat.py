from .base import *

# UAT Environment
DEBUG = False
ALLOWED_HOSTS = ['uat.yourdomain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.uat.sqlite3',
    }
}

# Logging configuration for UAT
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'uat.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
