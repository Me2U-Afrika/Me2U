"""
Django settings for Me2U project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'me2udev',
        'USER': os.environ.get('USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': 'localhost',
    }
}

LOGGING = {'handlers': {
    'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'verbose', },
},
    'loggers': {'django.db': {
        'handlers': ['console', ], 'level': 'DEBUG',
    },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

RAVE_SANDBOX = True
