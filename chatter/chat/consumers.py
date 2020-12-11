# Django
from django.template.loader import render_to_string

# Third Party Libraries
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# Local
from .models import Message
from .templatetags.chat import get_sidebar


class ChatConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def render_components(self, message):
        messages = (
            Message.objects.filter(room=message.room)
            .order_by("-created")
            .select_related("sender")[:9]
        )
        return {
            "messages": render_to_string(
                "chat/_messages.html", {"chat_messages": messages, "user": self.user}
            ),
            "sidebar": render_to_string(
                "chat/_sidebar.html",
                {"rooms": get_sidebar(self.user), "user": self.user},
            ),
        }

    @database_sync_to_async
    def get_message(self, message_id):
        """Get message if available to this user, or None"""
        try:
            return Message.objects.for_user(self.user).get(pk=message_id)
        except Message.DoesNotExist:
            return None

    async def connect(self):
        self.user = self.scope["user"]
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def chat_message(self, event):
        message = await self.get_message(event["message"]["id"])
        if message:
            components = await self.render_components(message)
            await self.send_json({**event, "components": components})
