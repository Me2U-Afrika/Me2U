from django import template
from django.contrib import messages
from django.dispatch import receiver
from django.utils import timezone
from me2ushop.models import Order, OrderItem, Product
from stats import stats
from stats.models import ProductView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in

import logging

from users.models import User

logger = logging.getLogger(__name__)

register = template.Library()


# @receiver(user_logged_in, sender=User)
# def merge_cart(sender, user, request, **kwargs):
#     print("we came here to merge")
#     if request.user.is_authenticated:
#         # print('request cart_id:', request.cart_id)
#
#         qs = Order.objects.filter(user=request.user, ordered=False)
#         # print(qs)
#         #
#         if request.cart:
#             print("before:", request.cart.id)
#             print("before orderID:", qs[0].id)
#
#             cart_id = request.cart
#             if cart_id.id != qs[0].id:
#
#                 order_items = OrderItem.objects.filter(order=cart_id, ordered=False)
#
#                 print('order_items:', order_items)
#
#                 for order_item in order_items:
#                     # print('item_cart_id:', order_item.cart_id)
#                     quantity = order_item.quantity
#
#                     # Get product instances for each
#                     product = Product.active.all()
#                     item = get_object_or_404(product, slug=order_item.item.slug)
#
#                     # Delete and create a new instance of the product
#                     order_item.delete()
#                     order_anonymous_delete = Order.objects.filter(id=cart_id.id, ordered=False)
#                     # # print("anonymous_id:", order_anonymous_delete)
#                     order_anonymous_delete.delete()
#                     # # print("anonymous_id:", order_anonymous_delete)
#                     #
#                     # # Add new product being ordered to database
#                     order_item, created = OrderItem.objects.get_or_create(
#                         item=item,
#                         user=request.user,
#                         ordered=False
#                     )
#                     # print("order_item:", order_item)
#                     # print("order_item_id:", order_item.cart_id)
#
#                     # Check if current user has products in cart
#                     order_query_set = Order.objects.filter(user=request.user, ordered=False)
#                     # print("user:", order_query_set)
#
#                     # This code returns the latest order by user that is not complete
#                     if order_query_set.exists():
#                         order = order_query_set[0]
#                         # order.items.add(order_item)
#                         # order.items = order_item
#                         # order.user = request.user
#                         # order.save()
#                         if order.items.filter(item__slug=item.slug).exists():
#                             if quantity > 1:
#                                 order_item.quantity += quantity
#                             else:
#                                 order_item.quantity += 1
#                             order_item.save()
#                         else:
#                             order.items.add(order_item)
#                             order_item.quantity = quantity
#                             order_item.save()
#                     else:
#                         # print("order not in cart")
#                         order_date = timezone.now()
#                         order = Order.objects.create(user=request.user, order_date=order_date)
#                         order.items.add(order_item)
#                         order_item.quantity = quantity
#                         order_item.save()
#                         order.save()
#                     request.session['cart_id'] = order.id
#         if qs:
#             return qs[0].items.count()
#         return 0


@register.filter
def cart_item_count(request):
    # if request.cart_id:
    #     qs = Order.objects.filter(cart_id=request.cart_id, ordered=False)
    #     if qs.exists():
    #         return qs[0].items.count()

    if request.cart:
        return request.cart.items.count()
    return 0


