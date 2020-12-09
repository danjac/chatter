# Django
from django.template.loader import render_to_string
from django.utils import timezone

# Third Party Libraries
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# Local
from .models import Message, Recipient, Room
from .templatetags.chat import get_sidebar


@database_sync_to_async
def get_rooms(user):
    return get_sidebar(user)


@database_sync_to_async
def get_room(room_id, user):
    # TBD: filter for user membership etc
    return Room.objects.get(pk=room_id)


@database_sync_to_async
def send_message(room, sender, text):
    Recipient.objects.filter(user=sender, message__room=room).update(
        read=timezone.now()
    )
    return room.create_message(sender, text)


@database_sync_to_async
def get_messages(room):
    return list(
        (
            Message.objects.filter(room_id=room.id)
            .select_related("sender")
            .order_by("-created")
        )[:9]
    )


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def chat_message(self, event):

        rooms = await get_rooms(self.user)

        await self.send_json(
            {
                **event,
                "fragments": {
                    **event["fragments"],
                    "sidebar": render_to_string("chat/_sidebar.html", {"rooms": rooms}),
                },
            }
        )

    async def receive_json(self, data):
        room_id = self.scope["url_route"]["kwargs"]["room_id"]

        text = data["text"]

        room = await get_room(room_id, self.user)
        await send_message(room, self.user, text)

        messages = await get_messages(room)

        await self.channel_layer.group_send(
            "chat",
            {
                "type": "chat.message",
                "fragments": {
                    f"room-{room.id}": render_to_string(
                        "chat/_messages.html", {"chat_messages": messages}
                    ),
                },
            },
        )
