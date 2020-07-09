from categories.models import Category
# from me2ushop.models import Product

from django.conf import settings


def me2u(request):

    return {'active_categories': Category.active.all(),
            'site_name': settings.SITE_NAME,
            'meta_keywords': settings.META_KEYWORDS,
            'meta_description': settings.META_DESCRIPTION,
            'request': request
            }
