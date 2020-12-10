# Third Party Libraries
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# Local
from .models import Message


@database_sync_to_async
def get_message(user, message_id):
    """Get message if available to this user, or None"""
    try:
        return Message.objects.for_user(user).get(pk=message_id)
    except Message.DoesNotExist:
        return None


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def chat_message(self, event):
        message = await get_message(self.user, event["message"]["id"])
        if message:
            await self.send_json(event)
