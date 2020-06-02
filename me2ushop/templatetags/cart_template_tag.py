from django import template
from me2ushop.models import Order
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

register = template.Library()


@login_required
@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()

    return 0
