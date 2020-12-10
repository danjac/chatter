# chat/routing.py
# Django
from django.urls import re_path

# Local
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/$", consumers.ChatConsumer.as_asgi()),
]
