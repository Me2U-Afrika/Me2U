from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.utils.html import format_html

from me2ushop.models import ProductImage, Product, Order, OrderItem, Address, Brand


@login_required()
def seller_page(request, slug):
    print('We are in the seller View')

    # from utils import context_processors
    # utils = context_processors.me2u(request)
    # brand = utils['brand']

    try:
        brand = Brand.objects.get(slug=slug, active=True)
        if brand:
            brand_id = brand.id

            print('user is an active seller')
            brand_name = brand

            # print(brand_name.id)

            products = brand_name.product_set.all()
            orders = OrderItem.objects.filter(item__in=products).filter(ordered=True).filter(status=10)
            items_delivered = OrderItem.objects.filter(item__in=products).filter(ordered=True).filter(status=50)
            # print('items:', items_delivered)

            # orders = Order.objects.filter(items__item__in=products).filter(ordered=True).filter(status=20).distinct()
            orders_completed = Order.objects.filter(items__item__in=products).filter(ordered=True).filter(
                status=30).distinct()

            order_id = Order.objects.filter(items__item__in=products, ordered=True).exclude(
                status__gt=20).distinct()

            total_orders = OrderItem.objects.filter(item__in=products, ordered=True)

            cancelled = total_orders.filter(status=40)
            delivered = OrderItem.objects.filter(status=50, item__in=products)
            pending = total_orders.filter(status=10)
            in_transit = total_orders.filter(status=45)
            page_title = 'Seller-Central'

            return render(request, 'sellers/seller_dashboard_template.html', locals())
            # return render(request, 'sellers/seller_test_page.html', locals())
        else:
            return redirect('me2ushop:brand_create')

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return redirect('me2ushop:home')


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
def seller_products(request, brand_id):
    user = request.user
    brand_id = brand_id
    products = Product.objects.filter(brand_name__id=brand_id)
    page_title = 'Seller Products'

    for obj in products:
        image = ProductImage.objects.filter(item=obj, in_display=True)
        if image:
            format_image = format_html(
                '<img src="%s"/>' % image[0].image.thumbnail.url
            )
            # print('product_image:', format_image)
            context = {
                'format_image': format_image,
            }

    return render(request, 'sellers/seller_products.html', locals())


def customer_details(request, id, template_name="sellers/customer_details_template.html"):
    print('we got here')
    from utils import context_processors
    context = context_processors.me2u(request)
    # brand_name = None
    brand_names = context['brand']

    if brand_names:
        brand_name = brand_names

        # products = brand_name.product_set.all()
        customer_orders = OrderItem.objects.filter(id=id)

        print('customer orders:', customer_orders)
        if customer_orders:
            for order in customer_orders:
                customer_email = order.customer_order.email
                customer_name = order.customer_order.name
                if order.user:
                    previous_orders = OrderItem.objects.filter(user=order.user, item__brand_name=brand_name)
                    # print('previous:', previous_orders)

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
    from utils import context_processors
    context = context_processors.me2u(request)
    brand_names = context['brand']
    page_title = 'Customer Address'

    if brand_names:
        brand_name = brand_names

    customer_address_info = Address.objects.filter(user__id=id)
    print('customer add:', customer_address_info)
    order = OrderItem.objects.filter(id=id)[0]

    return render(request, template_name, locals())
