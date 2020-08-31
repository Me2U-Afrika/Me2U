from django import template
from django.contrib import messages
from django.dispatch import receiver
from django.utils import timezone
from me2ushop.models import Order, OrderItem, Product
from stats import stats
from stats.models import ProductView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in

import logging

from users.models import User

logger = logging.getLogger(__name__)

register = template.Library()


@login_required
@register.filter
def cart_item_count(request, **kwargs):
    if request.user.is_authenticated:
        # print('request cart_id:', request.cart_id)

        qs = Order.objects.filter(user=request.user, ordered=False)
        # print(qs)
        #
        if request.cart_id:
            # print('true', request.cart_id)
            cart_id = request.cart_id
        #     # print("valid tracker:", cart_id.valid_tracker)
        #
        #     if cart_id.valid_tracker:
        #
            order_items = OrderItem.objects.filter(cart_id=cart_id, ordered=False)
        #
            # print('order_items:', order_items)
        #
            for order_item in order_items:
                # print('item_cart_id:', order_item.cart_id)
                quantity = order_item.quantity

                # Get product instances for each
                product = Product.active.all()
                item = get_object_or_404(product, slug=order_item.item.slug)
        #
                # Delete and create a new instance of the product
                order_item.delete()
                order_anonymous_delete = Order.objects.filter(cart_id=cart_id, ordered=False)
                # # print("anonymous_id:", order_anonymous_delete)
                order_anonymous_delete.delete()
                # # print("anonymous_id:", order_anonymous_delete)
                #
                # # Add new product being ordered to database
                order_item, created = OrderItem.objects.get_or_create(
                    item=item,
                    user=request.user,
                    ordered=False
                )
                # print("order_item:", order_item)
                # print("order_item_id:", order_item.cart_id)

                # Check if current user has products in cart
                order_query_set = Order.objects.filter(user=request.user, ordered=False)
                # print("user:", order_query_set)

                # This code returns the latest order by user that is not complete
                if order_query_set.exists():
                    order = order_query_set[0]
                    # order.items.add(order_item)
                    # order.items = order_item
                    # order.user = request.user
                    # order.save()
                    if order.items.filter(item__slug=item.slug).exists():
                        if quantity > 1:
                            order_item.quantity += quantity
                        else:
                            order_item.quantity += 1
                        order_item.save()
                    else:
                        order.items.add(order_item)
                        order_item.quantity = quantity
                        order_item.save()
                else:
                    # print("order not in cart")
                    order_date = timezone.now()
                    order = Order.objects.create(user=request.user, order_date=order_date)
                    order.items.add(order_item)
                    order_item.quantity = quantity
                    order_item.save()
                    order.save()
        #
        #     for tracking_id in request.cart_id:
        #         tracking_id.user = request.user
        #         tracking_id.valid_tracker = False
        #         tracking_id.save()
        #
        if qs:
            return qs[0].items.count()
        return 0


@register.filter
def cart_item_count_anonymous(request):
    if request.cart_id:
        qs = Order.objects.filter(cart_id=request.cart_id, ordered=False)
        if qs.exists():
            return qs[0].items.count()

    # if request.cart_order_id:
    #     # print('reqs:', request.cart_order_id.basketline_set.all().count())
    # return request.cart_order_id.basketline_set.all().count()
    # return request.cart_order_id.total_items()

    return 0

# @receiver(user_logged_in, sender=User)
# def merge_cart(sender, user, request, **kwargs):
#     print("we came here")
#     anonymous_cart = getattr(request, "cart_order_id", None)
#     print('anonymous cart:', anonymous_cart)
#     if anonymous_cart:
#         try:
#             loggdedin_cart = Basket.objects.get(user=user, status=Basket.OPEN)
#             print('curret cart:', loggdedin_cart)
#
#             for product in anonymous_cart.basketline_set.all():
#                 print('before', product )
#                 # print(product.cart)
#
#                 product.basket = loggdedin_cart
#                 print('new', product.basket)
#                 product.save()
#                 print('after', product)
#
#                 anonymous_cart.delete()
#                 request.cart_order_id = loggdedin_cart
#                 logger.info("Merged basket to id %d",
#                             loggdedin_cart.id)
#         except Basket.DoesNotExist:
#             anonymous_cart.user = user
#             anonymous_cart.save()
#             logger.info("Assigned user to basket id %d", anonymous_cart.id, )
