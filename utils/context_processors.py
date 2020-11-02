from categories.models import Category, Department
from me2ushop.models import Product, ProductReview, Brand
import os

from django.conf import settings

from stats import stats


def me2u(request):
    brand = None
    if request.user.is_authenticated and request.user.is_seller:
        brand = Brand.objects.get(user=request.user),
    print('utils brand:', brand)
    return {'active_categories': Category.active.all(),
            'active_departments': Department.active.all(),
            'reviews': ProductReview.objects.all().order_by('-date'),
            'recently_viewed': stats.get_recently_viewed(request),
            'brand': brand,
            'site_name': settings.SITE_NAME,
            'meta_keywords': settings.META_KEYWORDS,
            'meta_description': settings.META_DESCRIPTION,
            'request': request
            }


def globals(request):
    data = {}
    data.update({
        'VERSION': os.environ.get("GIT_REV", ""),  # available on every Dokku deployment
        'GA_TRACKER_ID': settings.GA_TRACKER_ID,
    })

    return data
