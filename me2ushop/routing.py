from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from . import consumers
from Me2U.auth import TokenGetAuthMiddlewareStack

websocket_urlpatterns = [
    re_path('ws/customer-service/(?P<order_id>[-\w]+)/$', consumers.ChatConsumer),

]

http_urlpatterns = [
    path('customer-service/notify/', AuthMiddlewareStack(
        consumers.ChatNotifyConsumer
    )),
    path('me2ushop/mobile-api/my-orders/<int:order_id>/tracker/',
         TokenGetAuthMiddlewareStack(consumers.OrderTrackerConsumer)),
]
