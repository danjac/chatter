# Third Party Libraries
# Django
from django.template.loader import render_to_string

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# Local
from .models import Message


class ChatConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def get_message(self, message_id):
        """Get message if available to this user, or None"""
        try:
            return (
                Message.objects.for_user(self.user)
                .select_related("sender", "room")
                .get(pk=message_id)
            )
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
            text = render_to_string("chat/_message.html", {"message": message})
            text = f'<turbo-stream target="messages" action="append"><template>{text}</template></turbo-stream>'
            await self.send({"type": "websocket.send", "text": text})
