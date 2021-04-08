# Third Party Libraries
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from turbo_response import TurboStream

# Local
from .models import Message
from .templatetags.chat import get_rooms


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

    @database_sync_to_async
    def get_rooms(self):
        return get_rooms(self.user)

    async def connect(self):
        self.user = self.scope["user"]
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def chat_message(self, event):
        message = await self.get_message(event["message"]["id"])
        rooms = await self.get_rooms()
        if message:
            await self.send(
                TurboStream("messages")
                .append.template(
                    "chat/_message.html", {"message": message, "user": self.user,},
                )
                .render()
            )
            await self.send(
                TurboStream("sidebar")
                .update.template("chat/_sidebar.html", {"rooms": rooms},)
                .render()
            )
