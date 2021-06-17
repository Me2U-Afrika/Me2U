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
        'brands': Brand.objects.filter(active=True),
        'site_name': settings.SITE_NAME,
        'LOGIN_URL': settings.LOGIN_URL,
        'meta_keywords': settings.META_KEYWORDS,
        'meta_description': settings.META_DESCRIPTION,
        'request': request

    }

    if request.user.is_authenticated and request.user.is_seller:
        try:
            brand = Brand.objects.filter(profile=request.user)
            # print('brand context:', brand)
            context.update({'user_brands': brand})
        except Exception:
            pass

    if request.user.is_authenticated:
        wish_list = WishList.objects.filter(user=request.user)

        if wish_list.exists():
            context.update({'wish_list': wish_list})

    try:
        session = request.session['tracking_id']
        if session:
            context.update({'recently_viewed': stats.get_recently_viewed(request)})
    except KeyError:
        context.update({'recently_viewed': None})

    banners = Banner.objects.filter(active=True)
    try:
        context.update({'trends': banners.filter(is_trending=True).select_related('product'),
                        'deals': banners.filter(is_deal=True).select_related('product')})
    except:
        pass
    return context


def globals(request):
    data = {}
    data.update({
        'VERSION': os.environ.get("GIT_REV", ""),  # available on every Dokku deployment
        'GA_TRACKER_ID': settings.GA_TRACKER_ID,
    })

    return data
