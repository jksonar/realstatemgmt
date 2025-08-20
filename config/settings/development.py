from .base import *

# Development Environment
DEBUG = True
ALLOWED_HOSTS = ['dev.yourdomain.com', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.parent / 'db.development.sqlite3',
    }
}

# Optional Redis caching for development
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# Logging configuration for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'development.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}