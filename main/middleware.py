from .models import *
from me2ushop.models import OrderItem, Order


def cart_middleware(get_response):
    def middleware(request):
        from stats import stats
        from stats.models import ProductView
        track_id = stats.tracking_id(request)
        try:
            cart_id = ProductView.objects.filter(tracking_id=track_id, valid_tracker=True)
            request.cart_id = cart_id
        except Exception:
            request.cart_id = track_id
        response = get_response(request)
        return response

    return middleware
