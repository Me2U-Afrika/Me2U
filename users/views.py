from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect

from .forms import UserRegisterForm
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from me2ushop.models import Order, OrderItem, Product
from .profile import retrieve_profile, set_profile
from .forms import AddressForm

# we going to create a view for register page using existing classes in django. The classes are converted to html.

def register(request):
    # create an instance of form
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        # Checking for validity
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!. You can now login!')
            return redirect('login')
    else:
        form = UserRegisterForm
        context = {
            'form': form,
            'page_title': 'User Registration'
        }
        page_title = 'User Registration'
        # context_instance = RequestContext(request)
        # print('contxt inst:', context_instance)
        return render(request, 'users/register.html', context)


@login_required()
def profile(request):
    page_title = 'My Account'
    orders = Order.objects.filter(user=request.user, ordered=True)
    # order_items = OrderItem.objects.filter(user=request.user, ordered=True)
    # print('orders:', orders)
    # print('order_items:', items)

    name = request.user.username
    # context_instance = RequestContext(request)
    # print('contxt inst profile:', context_instance)
    return render(request, 'users/profile.html', locals())


@login_required
def order_details(request, order_id, template_name="users/order-details.html"):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # print('order:', order)
    page_title = 'Order Details for Order #' + order_id
    order_items = OrderItem.objects.filter(user=request.user, order=order)
    # print('order_items:', order_items)
    # for order_item in order_items:
    # print('item:', order_item.item.slug)

    # context_instance = RequestContext(request)
    return render(request, template_name, locals())


@login_required
def re_order(request, order_id):
    # print("we in the re-order")
    # print('order id:', order_id)
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # print('order:', order)

    order_items = OrderItem.objects.filter(user=request.user, order=order)
    # print('order_items:', order_items)

    for order_item in order_items:
        # print('item:', item.quantity)
        quantity = order_item.quantity
        product = Product.active.all()
        item = get_object_or_404(product, slug=order_item.item.slug)
        # print("item found:", item)
        #
        # Add new product being ordered to database
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        # print("order_item:", order_item)

        # Check if current user has products in cart
        order_query_set = Order.objects.filter(user=request.user, ordered=False)
        # print("user:", order_query_set)

        # This code returns the user who ordered an item
        if order_query_set.exists():
            order = order_query_set[0]

            order.items.add(order_item)
            if quantity > 1:
                order_item.quantity = quantity
            else:
                order_item.quantity = 1
            order_item.save()

        else:
            # print("order not in cart")
            order_date = timezone.now()
            order = Order.objects.create(user=request.user, order_date=order_date)
            order.items.add(order_item)
            if quantity > 1:
                order_item.quantity = quantity
            else:
                order_item.quantity = 1
        order_item.save()
    messages.info(request, 'Your re-order cart has been updated!')
    return redirect("me2ushop:order_summary")


@csrf_protect
def order_info(request, template_name="users/order-info.html"):
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = AddressForm(postdata)
        if form.is_valid():
            set_profile(request)
            return redirect('users:profile')

    else:
        user_profile = retrieve_profile(request)
        print('user_profile:', user_profile)
        form = AddressForm(instance=user_profile)
        # print('form',form)
        page_title = 'Edit Order Information'
        context = {
            'form': form,
            'page_title': page_title
        }
        return render(request, template_name, context)
