from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import FormView
import datetime as dt
from django.contrib.auth.decorators import login_required

from . import forms
from .models import MaDere, Basket, BasketLine

# Create your views here.


from me2ushop.models import Product, OrderItem, Order


def welcome(request):
    return render(request, 'Me2U_home.html')


class ContactUsView(FormView):
    template_name = "contact_form.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


def add_to_cart(request):
    product = get_object_or_404(Product, pk=request.GET.get('product_id'))

    cart_order_id = request.cart_order_id
    print('cat:', cart_order_id)

    if not request.cart_order_id:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        cart_order_id = Basket.objects.create(user=user)
        # cart_order_id = Order.objects.create(user=user)

        # print('cart_items:', cart_order_id.id)
        request.session['cart_id'] = cart_order_id.id

    print('cat2:', cart_order_id)
    # order_item, created = BasketLine.objects.get_or_create(
    #     basket=cart_order_id.id,
    #     product=product
    # )
    # print('created:', created)

    order_item, created = BasketLine.objects.get_or_create(
        basket=cart_order_id,
        product=product,
    )
    print('created:', created)
    # print('created_id:', OrderItem.user)

    if not created:
        order_item.quantity += 1
        order_item.save()
        return redirect("me2ushop:order_summary")
    return redirect("me2ushop:product", slug=product.slug)


# We first update our news_today view function we call the render
# function and pass in 3 arguments. The request, the template file,
# and a dictionary of values that we pass into the template. This
# dictionary is referred to as the Context in Django and contains
# the context variables that are rendered inside the template.

@login_required()
def our_drivers(request):
    # day = convert_dates(date)
    date = dt.date.today()

    context = {
        'madriver': MaDere.objects.all()
    }

    return render(request, 'MaDriversWetu.html', context)

# the convert dates function is now being taken care of by the date filter in the base html

# def convert_dates(dates):
#     # get int of the day
#     day_number = dt.date.weekday(dates)
#
#     days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', "Sunday"]
#
#     # returning day
#     day = days[day_number]
#     return day

# @login_required()
# def past_days_news(request, past_date):
#     # pass
#     try:
#         # convert data from string to url
#         date = dt.datetime.strptime(past_date, '%Y-%m-%d').date()
#
#     except ValueError:
#         # raise 404 error when valueerror is thrown
#         raise Http404()
#         # assert False
#
#     # day = convert_dates(date)
#
#     if date == dt.date.today():
#         return redirect(news_of_day)
#
#     return render(request, 'all-main/past-main.html', {"date": date})
