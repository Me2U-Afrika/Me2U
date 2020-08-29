from rest_framework import serializers, viewsets
from . import models
from rest_framework.decorators import (api_view, permission_classes, )
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    item = serializers.StringRelatedField()

    class Meta:
        model = models.OrderItem
        fields = ('id', 'item', 'status')
        read_only_fields = ('id', 'item', 'status')


class PaidOrderItemsViewSet(viewsets.ModelViewSet):
    queryset = models.OrderItem.objects.filter(
        order__status=models.Order.PAID).order_by('-date_ordered')
    # print('queryset:', queryset)

    serializer_class = OrderItemSerializer
    filter_fields = ('item', 'status')


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Order
        fields = ('name',
                  'shipping_address1',
                  'shipping_address2',
                  'shipping_zip_code',
                  'shipping_city',
                  'shipping_country',
                  'start_date',
                  'order_date')


class PaidOrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.filter(
        status=models.Order.PAID).order_by('-order_date')
    serializer_class = OrderSerializer


# RETRIEVING ORDERS

@api_view()
@permission_classes((IsAuthenticated,))
def my_orders(request):
    user = request.user
    # orders = models.Order.objects.filter(user=user).order_by("-order_date")
    orders = models.OrderItem.objects.filter(user=user).order_by("-date_added")
    print('orders from test:', orders)
    data = []
    for order in orders:
        # for order in orders.items.all():
        data.append(
            {
                "id": order.id,
                'image': order.mobile_thumb_url,
                'summary': order.summary,
                'price': order.get_final_price(),

            }
        )
    # print(data)
    return Response(data)
