from django.conf import settings
from django.db.models import Max
from datetime import datetime, timedelta
from me2ushop.models import Order, OrderItem


def remove_old_cart_items():
    print('Removing old carts')
    print('session age:', settings.SESSION_AGE_DAYS)
    # calculate date of session age days ago
    remove_before = datetime.now() + timedelta(days=-settings.SESSION_AGE_DAYS)
    cart_ids = []
    old_items = Order.objects.values('id').annotate(last_change=Max('start_date')).filter(
        last_change__lt=remove_before).order_by()
    print('old items:', old_items)
    # create a list of cart ids that havent been modified
    for item in old_items:
        cart_ids.append(item['id'])
    to_remove = Order.objects.filter(id__in=cart_ids)
    print('to remove:', to_remove)
    for order in to_remove:
        order_items = order.items.all()
        print('order_items:', order_items)
        order_items.delete()

    to_remove.delete()
    print(str(len(cart_ids)) + "carts were removed")
