from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse
from django.utils.html import format_html
from users.models import User

from me2ushop.models import Product

from me2ushop.models import ProductImage, Product, Order, OrderItem, Address, Brand


@login_required()
def seller_page(request):
    # print('user:', request.user)
    # if not request.user.is_authenticated:
    #     return redirect('login/?next=/sellers/')
    if request.user.is_seller:
        try:
            from utils import context_processors
            utils = context_processors.me2u(request)
            brand_name = utils['brand'][0]
            print(brand_name.id)

            products = brand_name.product_set.all()
            orders = OrderItem.objects.filter(item__in=products).filter(ordered=True).filter(status=10)
            items_delivered = OrderItem.objects.filter(item__in=products).filter(ordered=True).filter(status=50)
            print('items:', items_delivered)

            # orders = Order.objects.filter(items__item__in=products).filter(ordered=True).filter(status=20).distinct()
            orders_completed = Order.objects.filter(items__item__in=products).filter(ordered=True).filter(
                status=30).distinct()
            print('orders:', orders)
            # print('order_id:', orders[0].id)
            # print('order_set:', orders[0].order_set.all())
            # customers = {}
            # order = Order.objects.filter(items__id=orders[0].id)
            # print('order:', order)
            # # print('order name:', order[0].user)
            # for order in order:
            #     if order.name not in customers:
            #         customers[order.user] = order.phone
            # print(customers)
            order_id = Order.objects.filter(items__item__in=products, ordered=True).exclude(
                status__gt=20).distinct()

            total_orders = OrderItem.objects.filter(item__in=products, ordered=True)
            # for order in total_orders:
            #     if order.user:
            #         customers[order.user] = order.order_set.get
            #         print('order.user:', order.user)
            #         print(customers)
            #     elif request.cart:
            #         customers['name'] = order.request.cart
            #         print('session cart id:', order.request.cart.id)
            cancelled = total_orders.filter(status=40)
            delivered = OrderItem.objects.filter(status=50, item__in=products)
            pending = total_orders.filter(status=10)
            in_transit = total_orders.filter(status=45)
            page_title = 'Seller-Central'

            return render(request, 'sellers/seller_dashboard_template.html', locals())
        except ObjectDoesNotExist:
            return redirect("users:brand_create")

    else:
        messages.warning(request, "You are not a registered Me2U seller Sign Up")
        return redirect('users:seller_create')


def automobile_page(request):
    print('user:', request.user)
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_dispatcher:
        orders = OrderItem.objects.filter(status=30).filter(ordered=True).exclude(order__status=30)
        # order_id = Order.objects.filter(ordered=True, status=20).distinct()

        # if order_id:
        #     order_id = order_id[0]
        # print('order_id', order_id[0].name)
        total_orders = OrderItem.objects.filter(delivered_by=request.user, status=50)
        pending = OrderItem.objects.filter(deliverd_by=request.user, status=45)
        delivered_by_me = OrderItem.objects.filter(status=50, delivered_by=request.user)
        print('delivered:', delivered_by_me)

        return render(request, 'automobiles/automobile_dashboard.html', locals())
    else:
        messages.warning(request, "You are not a registered Me2U delivery agent Sign Up")
        return redirect('users:automobile_create')


@login_required()
def seller_products(request):
    user = request.user
    products = Product.objects.filter(brand_name__user=user)

    for obj in products:
        image = ProductImage.objects.filter(item=obj, in_display=True)
        if image:
            format_image = format_html(
                '<img src="%s"/>' % image[0].image.thumbnail.url
            )
            # print('product_image:', format_image)
            context = {'format_image': format_image}

    return render(request, 'sellers/seller_products.html', locals())


def customer_details(request, id, template_name="sellers/customer_details_template.html"):
    print('we got here')
    from utils import context_processors
    context = context_processors.me2u(request)
    brand_name = context['brand'][0]
    products = brand_name.product_set.all()
    user_orders = OrderItem.objects.filter(id=id, item__in=products)
    print(user_orders)
    if user_orders:
        for user_order in user_orders:
            if user_order.user:
                customer_email = user_order.user.email
                customer_name = user_order.user.username

    # print('user_items:', user_orders)
    page_title = 'Customer Order Details'

    return render(request, template_name, locals())


def order_details(request, order_id, template_name="users/order-details.html"):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # print('order:', order)
    page_title = 'Order Details for Order #' + order_id
    order_items = OrderItem.objects.filter(user=request.user, order=order)
    seller_items = OrderItem.objects.filter(order=order, item__seller=request.user)

    print('seller_items:', order_items)
    # for order_item in order_items:
    # print('item:', order_item.item.slug)

    # context_instance = RequestContext(request)
    return render(request, template_name, locals())


def customer_address(request, id, template_name="sellers/customer_address.html"):
    customer_address_info = Address.objects.filter(user__id=id)
    print('customer add:', customer_address_info)
    user_orders = OrderItem.objects.filter(user_id=id, item__seller=request.user)
    print('user_items:', user_orders)
    orders = Order.objects.filter(user=id, items__item__seller=request.user)
    if orders:
        order = orders[0]

    return render(request, template_name, locals())
