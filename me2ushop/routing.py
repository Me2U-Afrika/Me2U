from channels.auth import AuthMiddlewareStack
from django.conf.urls import url
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/customer-service/(?P<order_id>[-\w]+)/$', consumers.ChatConsumer),

]

http_urlpatterns = [
    path('customer-service/notify/', AuthMiddlewareStack(
                consumers.ChatNotifyConsumer
        )),
]