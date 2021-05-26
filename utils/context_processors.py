from categories.models import Category, Department
from me2ushop.models import Product, ProductReview, Brand, WishList
import os

from django.conf import settings

from stats import stats
from marketing.models import *
from django.views.decorators.cache import cache_page

timeout = 600  # 10 min


def me2u(request):
    context = {
        'active_departments': Department.objects.filter(is_active=True),
        'reviews': ProductReview.objects.all().order_by('-date'),
        'recently_viewed': stats.get_recently_viewed(request),
        'brands': Brand.objects.filter(active=True),
        'trends': Banner.objects.filter(active=True, is_trending=True),
        'deals': Banner.objects.deals(),
        'site_name': settings.SITE_NAME,
        'LOGIN_URL': settings.LOGIN_URL,
        'meta_keywords': settings.META_KEYWORDS,
        'meta_description': settings.META_DESCRIPTION,
        'request': request

    }

    if request.user.is_authenticated and request.user.is_seller:
        try:
            user_brands = Brand.objects.filter(user__user=request.user)
            if user_brands:
                context.update({'user_brands': user_brands})
        except Exception:
            user_brands = None
            context.update({'user_brands': user_brands})

    if request.user.is_authenticated:
        wish_list = WishList.objects.filter(user=request.user)

        if wish_list.exists():
            context.update({'wish_list': wish_list})

    return context


def globals(request):
    data = {}
    data.update({
        'VERSION': os.environ.get("GIT_REV", ""),  # available on every Dokku deployment
        'GA_TRACKER_ID': settings.GA_TRACKER_ID,
    })

    return data
