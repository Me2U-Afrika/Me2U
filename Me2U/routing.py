from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.http import AsgiHandler
import me2ushop.routing
from .auth import TokenGetAuthMiddlewareStack

# (http--> django views is added by default)
application = ProtocolTypeRouter(
    {
        'websocket': TokenGetAuthMiddlewareStack(
            URLRouter(me2ushop.routing.websocket_urlpatterns)
        ),
        'http': URLRouter(
            me2ushop.routing.http_urlpatterns + [re_path(r"", AsgiHandler)]
        )
    })

