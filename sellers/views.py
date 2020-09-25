from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.utils.html import format_html
from users.models import User

from me2ushop.models import Product

from me2ushop.models import ProductImage, Product, Order, OrderItem, Address


def seller_page(request):
    print('user:', request.user)
    if not request.user.is_authenticated:
        return redirect('login/?next=/sellers/')
    if request.user.is_seller:
        items = OrderItem.objects.filter(item__seller=request.user).filter(ordered=True).exclude(status__gt=20)
        items_delivered = OrderItem.objects.filter(item__seller=request.user).filter(ordered=True).filter(status=50)
        print('items:', items_delivered)

        orders = Order.objects.filter(items__item__seller=request.user).filter(ordered=True).filter(status=20).distinct()
        orders_completed = Order.objects.filter(items__item__seller=request.user).filter(ordered=True).filter(status=30).distinct()
        print('orders:', orders)
        # print('order_id:', orders[0].id)
        # print('order_set:', orders[0].order_set.all())
        customers = {}
        order = Order.objects.filter(items__id=orders[0].id)
        print('order:', order)
        # print('order name:', order[0].user)
        for order in order:
            if order.name not in customers:
                customers[order.user] = order.phone
        print(customers)
        order_id = Order.objects.filter(items__item__seller=request.user, ordered=True).exclude(
            status__gt=20).distinct()

        total_orders = OrderItem.objects.filter(item__seller=request.user)
        # for order in total_orders:
        #     if order.user:
        #         customers[order.user] = order.order_set.get
        #         print('order.user:', order.user)
        #         print(customers)
        #     elif request.cart:
        #         customers['name'] = order.request.cart
        #         print('session cart id:', order.request.cart.id)
        cancelled = total_orders.filter(status=40)
        delivered = OrderItem.objects.filter(status=50, item__seller=request.user)
        pending = total_orders.filter(status=10)
        in_transit = total_orders.filter(status=45)

        return render(request, 'sellers/seller_dashboard.html', locals())
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


def seller_products(request):
    user = request.user
    seller_name = User.objects.get(email=user)
    products = Product.objects.filter(seller=seller_name)

    for obj in products:
        image = ProductImage.objects.filter(item=obj, in_display=True)
        if image:
            format_image = format_html(
                '<img src="%s"/>' % image[0].image.thumbnail.url
            )
            print('product_image:', format_image)
            context = {'format_image': format_image}

    # context = {
    #     'products': products,
    #     'service_providers': seller_name,
    # }
    print('seller_name:', seller_name.id)
    print('seller_products:', products)

    return render(request, 'sellers/seller_products.html', locals())


def customer_details(request, id, template_name="sellers/customer_details.html"):
    print('we got here')
    user_orders = OrderItem.objects.filter(id=id, item__seller=request.user)
    if user_orders:
        for user_order in user_orders:
            if user_order.user:
                ordered = Order.objects.filter(user=user_order.user)
                print(ordered)
                for user_order in ordered:
                    customer_email = user_order.user.email
                    customer_name = user_order.user.username
                    order = user_order
                    item = []
                    for items in order.items.all():
                        if items.item.seller == request.user:
                            item.append(items)
                            print('items:', item)
                            count = len(item)

            else:
                cart_id = user_order.cart_id
                order_id = Order.objects.filter(cart_id=cart_id)
                print('order_id:', order_id)

                for order_id in order_id:
                    print('order_id:', order_id)
                    customer_name = order_id.name
                    customer_email = order_id.email
                    # print('user_items:', order_id)

    print('user_items:', user_orders)
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
