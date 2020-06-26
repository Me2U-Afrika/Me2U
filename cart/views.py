from django.shortcuts import render
from django.template import RequestContext
from me2ushop.forms import CartAddProductForm
from me2ushop.models import OrderItem
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from .models import CartItem
from django.views.generic import ListView, DetailView, View

import random
import string


# Create your views here.

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def generate_cart_id():
    cart_id = random.choices(string.ascii_lowercase + string.digits, k=50)
    return cart_id


def cart_id_request(request):
    if 'cart_id' in request.session:
        request.session['cart_id'] = generate_cart_id()
    return request.session['cart_id']


class ShowCart(ListView):
    model = CartItem
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        total = 0
        context = super(ShowCart, self).get_context_data(**kwargs)
        cart_item_count = OrderItem.quantity
        # for item in cart_item_count:
        #     total += item
        page_title = 'Shopping Cart'
        context_instance = RequestContext(self.request)
        context['context_instance'] = context_instance
        context['page_title'] = page_title
        context['cart_item_count'] = cart_item_count

        return context
