import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'me2u',
        'USER': os.environ.get('USER'),
        'PASSWORD': os.environ.get('PASSWORD'),
        'HOST': 'localhost',
    }
}
#
# AWS_ACCESS_KEY_ID = 'AKIATXPOCGQKGV3H3N4S'
# AWS_SECRET_ACCESS_KEY = '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'
# AWS_STORAGE_BUCKET_NAME = "me2u-africa"
# PASSWORD = 'Welcome28@gmail'
# REDIS_URL = 'redis://localhost'
# SECRET_KEY = '*q^0ij+dl!102!@xhx-4o7%am5(tiof2d_#)g*cehlw!3z98_!'
# STRIPE_PUBLISHABLE_KEY = 'pk_test_9or5EaMyoLjRYXOXKfQp16ab00YxYjqkzO'
# STRIPE_SECRET_KEY = 'sk_test_zI4rsVZHDZLSyWxazI986czl00mW4RjtRt'
# DEBUG = bool(os.environ.get('LOCAL_DEBUG', ''))
#
