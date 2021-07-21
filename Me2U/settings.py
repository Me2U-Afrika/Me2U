"""
Django settings for Me2U project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import django_heroku
import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
# print('env:', env)
environ.Env.read_env()

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = os.environ.get('SECRET_KEY')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

AUTH_PROFILE_MODULE = 'users.profile'
AUTH_USER_MODEL = 'users.User'

ADMINS = (
    ('Me2U|Africa IT', 'danielmakori0@gmail.com'),
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
ALLOWED_HOSTS = ['me2uafrica.herokuapp.com', '127.0.0.1:8000', 'me2uafrika.com', 'www.me2uafrika.com']

CANON_URL_HOST = 'www.me2uafrika.com'
CANON_URLS_TO_REWRITE = ['me2uafrika.com', 'me2uafrica.herokuapp.com']

# SECURITY WARNING: don't run with debug turned on in production!
# False if not in os.environ
DEBUG = env('DEBUG')
#
# DEBUG = False
# print('debug:', DEBUG)

SITE_URL = 'https://www.me2uafrika.com'

if DEBUG:
    SITE_URL = 'http://127.0.0.1:8000'

EMAIL_SUBJECT_PREFIX = '[Me2U|Afrika]'

# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'channels',
    'categories',
    'currencies',
    # 'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.redirects',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_social_share',

    'asymmetric_jwt_auth',
    'certbot_django.server',

    'django_extensions',
    'django_filters',
    'debug_toolbar',
    'widget_tweaks',
    'django_tables2',
    'django.contrib.sitemaps',
    # 'django_memcached',
    'memcache_status',
    # 'redis_cache',
    'djangorave',
    'blog',
    'main',
    'bootstrap3',
    'bootstrap4',
    'users.apps.UsersConfig',
    'me2ushop',
    'marketing',
    'crispy_forms',
    'django_countries',
    'stripe',
    'utils',
    'mptt',
    "django_mptt_admin",
    'search',
    'sellers',
    'stdimage',
    'stats',
    'tagging',
    'storages',
    'rest_framework',
    'rest_framework.authtoken',
    'webpack_loader',
    'ckeditor',
    'ckeditor_uploader',
    'payments',

]

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'extraPlugins': ','.join(
                    [
                        'codesnippet',
                        'youtube'
                    ]
                ),
    },

    'Special': {
        'toolbar': 'Special',
        'toolbar_Special': [

            ['-', 'Outdent', 'Indent', '-', 'JustifyLeft',
             'JustifyBlock'],
            ['RemoveFormat', 'Source']
        ]
    }

}

DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap.html'

# default is 10 pixels
MPTT_ADMIN_LEVEL_INDENT = 20

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':
        ('rest_framework.authentication.SessionAuthentication',
         'rest_framework.authentication.TokenAuthentication',
         'rest_framework.authentication.BasicAuthentication',),

    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination', 'PAGE_SIZE': 100

}

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    # "sslify.middleware.SSLifyMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'Me2U.SSLMiddleware.SSLRedirect',
    'main.middleware.cart_middleware',
    # 'marketing.urlcanon.URLCanonicalizationMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'asymmetric_jwt_auth.middleware.JWTAuthMiddleware',

]
# if DEBUG:
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'


servers = os.environ['MEMCACHIER_SERVERS']
username = os.environ['MEMCACHIER_USERNAME']
password = os.environ['MEMCACHIER_PASSWORD']

CACHES = {
    'default': {
        # Use django-bmemcached
        'BACKEND': 'django_bmemcached.memcached.BMemcached',

        # TIMEOUT is not the connection timeout! It's the default expiration
        # timeout that should be applied to keys! Setting it to `None`
        # disables expiration.
        # 'TIMEOUT': None,
        'TIMEOUT': 600,

        'LOCATION': servers,

        'OPTIONS': {
            'username': username,
            'password': password,
        }
    }
}

# CACHE_MIDDLEWARE_SECONDS = 2


INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'Me2U.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'utils.context_processors.me2u',
                'utils.context_processors.globals',
                'currencies.context_processors.currencies',

            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ]

        },
    },
]

WEBPACK_LOADER = {
    'DEFAULT': {'BUNDLE_DIR_NAME': 'bundles/',
                'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
                }
}

WSGI_APPLICATION = 'Me2U.wsgi.application'
ASGI_APPLICATION = 'Me2U.routing.application'

REDIS_URL = os.environ.get('REDIS_URL')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}
SITE_ID = 1
GA_TRACKER_ID = '123'

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'me2u',
            'USER': os.environ.get('USER'),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
            'HOST': 'localhost',
        }
    }
    import dj_database_url

    db_from_env = dj_database_url.config(conn_max_age=600)
    DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

OPENEXCHANGERATES_APP_ID = os.environ.get('OPENEXCHANGERATES_APP_ID')

DEFAULT_CURRENCY = 'USD'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

SITE_NAME = 'Me2U|Afrika'
META_KEYWORDS = 'ONLINE MARKET, AFRICA BIGGEST ECOMMERCE, BUY ONLINE TODAY'
META_DESCRIPTION = 'Me2U|Afrika is an online self sustaining ecommerce tailored towards delivering best services and ' \
                   'products' \
                   'Across the globe with a major focus in African Markets.'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = 'me2ushop:home'
LOGIN_URL = 'account_login'

RAVE_PRODUCTION_PUBLIC_KEY = os.environ.get('RAVE_PRODUCTION_PUBLIC_KEY')
RAVE_PRODUCTION_SECRET_KEY = os.environ.get('RAVE_PRODUCTION_SECRET_KEY')
RAVE_SANDBOX_PUBLIC_KEY = os.environ.get('RAVE_SANDBOX_PUBLIC_KEY')
RAVE_SANDBOX_SECRET_KEY = os.environ.get('RAVE_SANDBOX_SECRET_KEY')
RAVE_SANDBOX = False

ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = None

SOCIALACCOUNT_ADAPTER = 'users.adapter.MySocialAccountAdapter'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'Me2U.storage.WhiteNoiseStaticFilesStorage'

# stripe settings

if DEBUG:
    # test keys

    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_kEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

else:
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    # STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # DEFAULT_FILE_STORAGE = 'Me2U.storage.MediaStorage'

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None

    # AWS_FILE_EXPIRE = 200
    # AWS_PRELOAD_METADATA = True
    # AWS_QUERYSTRING_AUTH = False

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # CORS_REPLACE_HTTPS_REFERER = True
    # HOST_SCHEME = 'https://'
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_SECONDS = 1000000
    # SECURE_FRAME_DENY = True

    # turn to true during production
    # ENABLE_SSL = False

# Email Config
# Email server

# MAILGUM SMTP WORKING
# MAILGUN_ACCESS_KEY = os.environ.get('MAILGUN_ACCESS_KEY', '')
# MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', '')
# MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', '')
# EMAIL_HOST = os.environ.get('MAILGUN_SMTP_SERVER', '')
# EMAIL_PORT = os.environ.get('MAILGUN_SMTP_PORT', '')
# EMAIL_HOST_USER = os.environ.get('MAILGUN_SMTP_LOGIN', '')
# EMAIL_HOST_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD', '')


# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.environ.get('PASSWORD')
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
# SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
# SENDGRID_SANDBOX_MODE_IN_DEBUG = False
#
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
# EMAIL_PORT = 587
MAILGUN_ACCESS_KEY = os.environ.get('MAILGUN_ACCESS_KEY', '')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', '')
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', '')
EMAIL_HOST = os.environ.get('MAILGUN_SMTP_SERVER', '')
EMAIL_PORT = os.environ.get('MAILGUN_SMTP_PORT', '')
EMAIL_HOST_USER = os.environ.get('MAILGUN_SMTP_LOGIN', '')
EMAIL_HOST_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD', '')

EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

PRODUCTS_PER_PAGE = 12
PRODUCTS_PER_ROW = 12

CRISPY_TEMPLATE_PACK = "bootstrap4"

try:
    from settings_local import *
except ImportError:
    pass

# print(e.message)
# Activate Django-Heroku.
django_heroku.settings(locals())

# add ENV=development in the .env file for the below to work:
if not DEBUG:
    del DATABASES['default']['OPTIONS']['sslmode']
