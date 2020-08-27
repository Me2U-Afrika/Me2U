from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.utils.html import format_html
from users.models import User

from me2ushop.models import Product

from me2ushop.models import ProductImage, Product, Order, OrderItem, Address


def seller_page(request):
    print('user:', request.user)
    orders = OrderItem.objects.filter(item__seller=request.user).filter(ordered=True).exclude(order__status=30).exclude(status__gt=20)
    order_id = Order.objects.filter(items__item__seller=request.user, ordered=True, status=20).distinct()

    # if order_id:
    #     order_id = order_id[0]
    # print('order_id', order_id[0].name)
    total_orders = Order.objects.filter(items__item__seller=request.user)
    cancelled = Order.objects.filter(items__item__seller=request.user, items__status=40)
    delivered = Order.objects.filter(items__status=30, status=30, items__item__seller=request.user)
    pending = orders.exclude(order__status=30)
    print('orders:', orders)
    for order in orders:
        if order.user:
            print(order.user)
        else:
            print(order.cart_id)
    # for order in order_id:
    #     print('order number:', order)
    #     print('order from id:', order.items.all())
    print('delivered:', delivered)
    print('pending:', pending.count())

    return render(request, 'sellers/seller_dashboard.html', locals())


def seller_products(request):
    user = request.user
    seller_name = User.objects.get(email=user)
    products = Product.objects.filter(seller=seller_name)

    for obj in products:
        image = ProductImage.objects.filter(item=obj, in_display=True)[0]
        if image:
            format_image = format_html(
                '<img src="%s"/>' % image.image.thumbnail.url
            )
            print('product_image:', format_image)
            context = {'format_image': format_image}

    # context = {
    #     'products': products,
    #     'seller': seller_name,
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
