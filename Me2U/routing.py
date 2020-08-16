from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.http import AsgiHandler
from me2ushop import routing

# (http--> django views is added by default)
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(routing.websocket_urlpatterns)
    ),
    'http': URLRouter(
        routing.http_urlpatterns + [re_path(r"", AsgiHandler)]
    )
})
