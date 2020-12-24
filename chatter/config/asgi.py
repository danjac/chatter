# Standard Library
import os

# Django
from django.core.asgi import get_asgi_application

# Third Party Libraries
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

# Chatter
from chatter.chat import routing as chat_routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatter.config.settings.local")


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        # Just HTTP for now. (We can add other protocols later.)
        "websocket": AuthMiddlewareStack(URLRouter(chat_routing.websocket_urlpatterns)),
    }
)
