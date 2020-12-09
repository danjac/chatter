# Django
from django.utils import timezone

# Third Party Libraries
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# Local
from .models import Recipient, Room


@database_sync_to_async
def get_room(room_id, user):
    # TBD: filter for user membership etc
    try:
        return Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        return None


@database_sync_to_async
def send_message(room, sender, text):
    Recipient.objects.filter(user=sender, message__room=room).update(
        read=timezone.now()
    )
    return room.create_message(sender, text)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def chat_message(self, event):
        await self.send_json(event)

    async def receive_json(self, data):
        room_id = self.scope["url_route"]["kwargs"]["room_id"]

        text = data["text"]

        room = await get_room(room_id, self.user)
        await send_message(room, self.user, text)

        await self.channel_layer.group_send(
            "chat",
            {
                "type": "chat.message",
                "room": f"room-{room.id}",
                "message": {"sender": self.user.username, "text": text,},
            },
        )
