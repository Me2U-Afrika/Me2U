from categories.models import Category
# from me2ushop.models import Product
import os

from django.conf import settings


def me2u(request):
    return {'active_categories': Category.active.all(),
            'site_name': settings.SITE_NAME,
            'meta_keywords': settings.META_KEYWORDS,
            'meta_description': settings.META_DESCRIPTION,
            'request': request
            }


def globals(request):
    data = {}
    data.update({
        'VERSION': os.environ.get("GIT_REV", ""),  # available on every Dokku deployment
        'GA _TRACKER_ID': settings.GA_TRACKER_ID,
    })

    return data
