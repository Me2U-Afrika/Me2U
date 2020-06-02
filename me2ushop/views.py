from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .forms import CheckoutForm, CouponForm, CartAddProductForm
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from .models import Item, OrderItem, Order, BillingAddress, StripePayment, Coupon
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponse

import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class HomeView(ListView):
    model = Item
    paginate_by = 5
    template_name = 'home-page.html'


class ItemDetailedView(DetailView):
    model = Item
    template_name = 'product-page.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super(ItemDetailedView, self).get_context_data(**kwargs)
        cart_product_form = CartAddProductForm()
        context['cart_product_form'] = cart_product_form
        return context


class Order_summary_view(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
            return redirect("me2ushop:home")


class Checkout_page(View):
    def get(self, *args, **kwargs):
        #     form we made for checkout

        form = CheckoutForm()

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            context = {
                'object': order,
                'form': form,
                'couponform': CouponForm,
                'DISPLAY_COUPON_FORM': True,
            }
            return render(self.request, 'checkout-page.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
            return redirect("me2ushop:home")

        except Exception:
            messages.info(self.request, 'Login to perform function ')
            return redirect("me2ushop:home")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')

                # TODO: add functionality for these fields
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')

                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )

                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO: add a redirect to the selected payment option
                if payment_option == 'S':
                    return redirect("me2ushop:payment", payment_option='stripe')
                elif payment_option == 'P':
                    return redirect("me2ushop:payment", payment_option='paypal')
                elif payment_option == 'M':
                    return redirect("me2ushop:payment", payment_option='mpesa')
                elif payment_option == 'C':
                    return redirect("me2ushop:payment", payment_option='cash_on_delivery')
                else:
                    messages.warning(self.request, 'Invalid Payment Option. Select mode of payment to continue')
                    return redirect("me2ushop:checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
            return redirect("me2ushop:home")


class PaymentView(View):

    def get(self, *args, **kwargs):

        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'object': order,
                'DISPLAY_COUPON_FORM': False

            }
            return render(self.request, 'payment.html', context)
        else:
            messages.warning(self.request, "Please fill in your shipping address prior to payment")
            return redirect("me2ushop:checkout")

    def post(self, *args, **kwargs):
        # `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

        if self.request.method == 'POST':

            order = Order.objects.get(user=self.request.user, ordered=False)

            amount = int(order.get_total() * 100)  # get in ksh
            token = self.request.POST['stripeToken']
            # token = self.request.POST.get('stripeToken')

            try:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=token,
                )

                # create payment
                payment = StripePayment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = amount
                payment.save()
                #
                #     # Assign payment to user

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    print('item:', item)
                    item.save()

                order.ordered = True
                order.stripe_payment = payment

                # Assigning the order a ref code during checkout payment

                order.ref_code = create_ref_code()
                order.save()

                if order.ordered:
                    order.coupon.valid = False
                    order.coupon.save()

                messages.success(self.request, " CONGRATULATIONS YOUR ORDER WAS SUCCESSFUL")
                return redirect("me2ushop:home")
            #
            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body
                err = body.get('error', {})
                messages.error(self.request, f"{err.get('message')}")
                return redirect("me2ushop:home")

            except stripe.error.RateLimitError as e:
                messages.error(self.request, "Rate Limit Error ")
                return redirect("me2ushop:home")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.error(self.request, "Invalid parameters")
                return redirect("me2ushop:home")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.error(self.request, "Not authenticated")
                return redirect("me2ushop:home")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.error(self.request, "Network error ")
                return redirect("me2ushop:home")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.error(self.request,
                               "Something went wrong. You were not charged. Please try again or contact us")
                return redirect("me2ushop:home")

            except Exception as e:
                # Something else happened, completely unrelated to Stripe
                messages.error(self.request, "Serious error occurred, we have been notified ")
                return redirect("me2ushop:home")

        return redirect("me2ushop:home")


def product_page(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        # order_item = OrderItem.objects.get(user=request.user, ordered=False)

        context = {
            'item': Item.objects.all(),
            'object': order,
            'order_item': OrderItem.objects.all()
        }
        return render(request, 'product-page.html', context)
    except Exception:
        return render(request, 'product-page.html')


# @login_required()
def add_cart(request, slug):
    # if request.user.is_anonymous:
    messages.info(request, "You in the add cart but not add cart qty")
    try:
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_query_set = Order.objects.filter(user=request.user, ordered=False)

        if order_query_set.exists():
            order = order_query_set[0]

            # check if the order item is in the order

            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, 'This item quantity was updated.')
                return redirect("me2ushop:order_summary")
            else:
                messages.info(request, 'This item has been added to your cart.')
                order.items.add(order_item)
                order_item.quantity = 1
                order_item.save()
                return redirect("me2ushop:order_summary")
        else:
            order_date = timezone.now()
            order = Order.objects.create(user=request.user, order_date=order_date)
            order.items.add(order_item)
            order_item.quantity = 1
            order_item.save()
            messages.info(request, 'This item has been added to your cart.')
            return redirect("me2ushop:order_summary")

    except Exception:
        messages.warning(request, 'Order not recorded, Login to continue. QuiQ and Eazzay')
        # add_cart_product(request, slug)
        return redirect("me2ushop:product", slug=slug)


# @login_required()
def remove_cart(request, slug):
    try:
        item = get_object_or_404(Item, slug=slug)

        order_query_set = Order.objects.filter(
            user=request.user,
            ordered=False)

        if order_query_set.exists():
            order = order_query_set[0]
            #         check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                while order_item.quantity > 0:
                    order_item.quantity -= 1

                    if order_item.quantity == 0:
                        order.items.remove(order_item)
                        messages.info(request, 'This item was removed from your cart.')
                        order_item.save()
                        return redirect("me2ushop:product", slug=slug)
                return redirect("me2ushop:product", slug=slug)

            else:
                # add message saying no order for user
                messages.info(request, 'This item is not in your cart.')
                return redirect("me2ushop:product", slug=slug)

        else:
            # add message saying no order for user
            messages.info(request, 'You do not have an active order.')
            return redirect("me2ushop:product", slug=slug)

    except Exception:
        messages.warning(request, 'Login to continue')
        return redirect("me2ushop:product", slug=slug)


@login_required()
def remove_single_item_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_query_set = Order.objects.filter(
        user=request.user,
        ordered=False)

    if order_query_set.exists():
        order = order_query_set[0]

        #         check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            print('order_item:', order_item)

            if order_item.quantity >= 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'This item quantity has been reduced.')
                # redirect("me2ushop:order_summary")

                if order_item.quantity == 0:
                    order.items.remove(order_item)
                    messages.info(request, 'This item has been deleted from your cart.')
                    return redirect("me2ushop:product", slug=slug)

            return redirect("me2ushop:order_summary")

    return redirect("me2ushop:product", slug=slug)


# def add_cart_product(request, slug):
#     if request.method == "POST":
#         messages.info(request, "we in the add_cart_product page function, working so far")
#
#         item = get_object_or_404(Item, slug=slug)
#
#         form = CartAddProductForm(request.POST or None)
#         if form.is_valid():
#
#             # Get quantity of the item ordered so far
#             qty = form.cleaned_data.get('quantity')
#             print("qty:", qty)
#
#             new_qty = qty + 3
#             form.quantity = new_qty
#             update = form.cleaned_data.get('quantity')
#             print("update:", update)
#             return redirect("me2ushop:product", slug=slug)
#         return redirect("me2ushop:product", slug=slug)
#     return redirect("me2ushop:product", slug=slug)


#     order_item, created = OrderItem.objects.get_or_create(
#         item=item,
#         ordered=False)
#     order_query_set = Order.objects.filter(ordered=False)
#
#     if order_query_set.exists():
#         order = order_query_set[0]
#
#         # check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item.quantity += 1
#             order_item.save()
#             messages.info(request, 'Your Order quantity was updated.')
#             return redirect("me2ushop:product", slug=slug)
#         else:
#             messages.info(request, 'This item has been added to your cart.')
#             order.items.add(order_item)
#             order_item.quantity = 1
#             order_item.save()
#             return redirect("me2ushop:product", slug=slug)
#
#     else:
#         order_date = timezone.now()
#         order = Order.objects.create(order_date=order_date)
#         order.items.add(order_item)
#         order_item.quantity = 1
#         order_item.save()
#         messages.info(request, 'This item has been added to your cart.')
#         return redirect("me2ushop:product", slug=slug)


# def remove_single_item_cart_product(request, slug):
#     item = get_object_or_404(Item, slug=slug)
#
#     order_query_set = Order.objects.filter(
#         user=request.user,
#         ordered=False)
#
#     if order_query_set.exists():
#         order = order_query_set[0]
#         print('order:', order)
#
#         #         check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item = OrderItem.objects.filter(
#                 item=item,
#                 user=request.user,
#                 ordered=False
#             )[0]
#
#             if order_item.quantity >= 1:
#                 order_item.quantity -= 1
#                 order_item.save()
#                 messages.info(request, 'This item was reduced.')
#
#                 if order_item.quantity == 0:
#                     order.items.remove(order_item)
#                     messages.info(request, 'Note that the item has been removed from your cart.')
#                     return redirect("me2ushop:product", slug=slug)
#         else:
#             messages.info(request, 'You do not have an active order.')
#             return redirect("me2ushop:product", slug=slug)
#     messages.warning(request, 'You need to be logged in')
#     return redirect("me2ushop:product", slug=slug)

#
# def cart_item_count(user):
#     if user.is_authenticated:
#         query_set = Order.objects.filter(user=user, ordered=False)
#         if query_set.exists():
#             return query_set[0].items.count()
#
#     return 0

def get_coupon(request, code):
    try:
        # we take the online provided code and run it through our available coupons in order to determine it's value
        coupon = Coupon.objects.get(code=code)

        print("coupon from get method:", coupon)
        if coupon.valid:
            return coupon
        else:
            messages.info(request, 'This coupon is already depleted. Tafuta ingine mazee')
            return redirect('me2ushop:checkout')

    except ObjectDoesNotExist:
        messages.warning(request, 'Tumekosa hii ticket kwa system')
        return redirect('me2ushop:checkout')


def add_coupon(request):
    if request.method == "POST":
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                # get the order
                order = Order.objects.get(user=request.user, ordered=False)

                if order.total_items() > 0:
                    print("The number of orders in the cart:", order.total_items())

                    # Get code coupon provided online
                    code = form.cleaned_data.get('code')

                    print("coode:", code)

                    # Get existing coupons we have in the system if they match
                    coupon_id = get_coupon(request, code)
                    print("coupon id:", coupon_id)

                    order.coupon = coupon_id
                    messages.success(request,
                                     'Coupon was successful, thank you for joining Me2U Africa. KARIBU')
                    order.save()

                    # item.valid = False
                    # item.save()
                    return redirect('me2ushop:checkout')

                else:
                    messages.info(request, 'You don\'t have an active order')
                    return redirect('me2ushop:order_summary')

            except Exception:
                messages.warning(request, 'Ticket used already')
                return redirect('me2ushop:checkout')

        # order.coupon = coupon_id
        # print(" Coupon ID FETCHED", coupon_id)
        # order.save()
        # coupon_validity = Coupon.objects.all()
        # print("couponvalidty:", coupon_validity)
        # for item in coupon_validity:
        #     print("item:", item)
        #     if item == coupon_id:
        #         if item.valid:
        #             order.coupon = coupon_id
        #             messages.success(request,
        #                              'Coupon was successful, thank you for joining Me2U Africa. KARIBU')
        #             order.save()
        #             # Change coupon to invalid
        #             item.valid = False
        #             item.save()
        #             return redirect('me2ushop:checkout')
        #         else:
        #             messages.warning(request, 'The coupon has been already utilized')
        #             return redirect('me2ushop:checkout')
        #     else:
        #         messages.warning(request, 'The coupon code is invalid')
        #         return redirect('me2ushop:checkout')
    #             return redirect('me2ushop:checkout')
    #         except ObjectDoesNotExist:
    #             messages.info(request, 'You do have an active order')
    #             return redirect('me2ushop:order_summary')
    #     return redirect('me2ushop:checkout')
    # return redirect('me2ushop:checkout')


def add_cart_qty(request, slug):
    # messages.info(request, "we came here and still here")

    if request.method == "POST":
        # messages.info(request, "we in the add_cart function, working so far")

        form = CartAddProductForm(request.POST or None)
        if form.is_valid():

            try:
                # Get quantity from useronline

                qty = form.cleaned_data.get('quantity')
                # print("qty:", qty)

                # Determine the item and assign quantity provieded by user to their cart.

                item = get_object_or_404(Item, slug=slug)
                order_item, created = OrderItem.objects.get_or_create(
                    item=item,
                    user=request.user,
                    ordered=False,
                )

                # print("order_item:", order_item)

                order_query_set = Order.objects.filter(user=request.user, ordered=False)
                # print("This user has the following orders:", order_query_set)
                #
                if order_query_set.exists():
                    order = order_query_set[0]

                    # check if this specific order item is in the order in order to increment it or update it

                    if order.items.filter(item__slug=item.slug).exists():
                        order_item.quantity = qty
                        order_item.save()
                        messages.info(request, 'This item quantity has been updated.')
                        return redirect("me2ushop:order_summary")
                    else:
                        messages.info(request, 'This item has been added to your cart.')
                        order.items.add(order_item)
                        order_item.quantity = qty
                        order_item.save()
                        return redirect("me2ushop:order_summary")
                else:
                    order_date = timezone.now()
                    order = Order.objects.create(user=request.user, order_date=order_date)
                    order.items.add(order_item)
                    order_item.quantity = qty
                    order_item.save()
                    messages.info(request, 'This item has been added to your cart.')
                    return redirect("me2ushop:order_summary")

            except Exception:
                messages.warning(request, 'no data yet')
                return redirect('me2ushop.order_summary')

    messages.warning(request, "Something is a miss here!")
    return redirect('me2ushop:home')

    # form = CartAddProductForm(request.POST or None)
    # if form.is_valid():
    #
    #     try:
    #
    #         # Get quantity from useronline
    #         qty = form.cleaned_data.get('code')
    #         print("qty:", qty)
    #
    #         # post to our database
    #         recored_qty = post_cart_qty(request, qty)
    #         print("recorded_qty:", recored_qty)
    #
    #         item = get_object_or_404(Item, slug=slug)
    #         order_item, created = OrderItem.objects.get_or_create(
    #             item=item,
    #             user=request.user,
    #             ordered=False
    #         )
    #         order_query_set = Order.objects.filter(user=request.user, ordered=False)
    #
    #         if order_query_set.exists():
    #             order = order_query_set[0]
    #
    #             # check if the order item is in the order
    #
    #             if order.items.filter(item__slug=item.slug).exists():
    #                 order_item.quantity += recored_qty
    #                 order_item.save()
    #                 messages.info(request, 'This item quantity was updated.')
    #                 return redirect("me2ushop:order_summary")
    #             else:
    #                 messages.info(request, 'This item has been added to your cart.')
    #                 order.items.add(order_item)
    #                 order_item.quantity = recored_qty
    #                 order_item.save()
    #                 return redirect("me2ushop:order_summary")
    #         else:
    #             order_date = timezone.now()
    #             order = Order.objects.create(user=request.user, order_date=order_date)
    #             order.items.add(order_item)
    #             order_item.quantity = recored_qty
    #             order_item.save()
    #             messages.info(request, 'This item has been added to your cart.')
    #             return redirect("me2ushop:order_summary")
    #
    #     except Exception:
    #         messages.warning(request, 'no data yet')
    #         return redirect('me2ushop.order_summary')
    #
