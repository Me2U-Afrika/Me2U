from utils.views import user_location
from .models import *
from me2ushop.models import OrderItem, Order
from django.db import close_old_connections
import random
import string


# CART_ID_SESSION_KEY = 'cart_id'
#
#
# def _cart_id(request):
#     # print(' before request found:', request.session.get(CART_ID_SESSION_KEY))
#
#     if request.session.get(CART_ID_SESSION_KEY, '') == '':
#         request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
#     return request.session[CART_ID_SESSION_KEY]
#
#
# def _generate_cart_id():
#     cart_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
#     return cart_id
#
#
# def cart_middleware(get_response):
#     def middleware(request):
#         # from stats import stats
#         # from stats.models import ProductView
#         # track_ids = stats.tracking_id(request)
#         # track_id = ''
#         # if track_ids:
#         #     track_id = track_ids[0]
#         # try:
#         #     cart_id = ProductView.objects.filter(tracking_id=track_id, valid_tracker=True)
#         #     request.cart_id = cart_id
#         # except Exception:
#         #     request.cart_id = track_id
#         try:
#             request.cart_id = _cart_id(request)
#         except Exception:
#             request.cart_id = None
#
#         # print(request.cart_id)
#         response = get_response(request)
#         return response
#
#     return middleware


def cart_middleware(get_response):
    def middleware(request):
        # print('we came to cart middleware')

        if 'cart_id' in request.session:
            cart_id = request.session['cart_id']
            if cart_id:
                try:
                    cart = Order.objects.get(id=cart_id)
                    request.cart = cart
                except Exception:
                    request.cart = None
        else:
            request.cart = None

        if 'country' in request.session:
            request.country = request.session['country']
        else:
            # print('no country')
            request.country = None
            user_location(request)
        response = get_response(request)
        return response

    return middleware


