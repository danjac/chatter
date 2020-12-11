# Third Party Libraries
import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator

# Chatter
from chatter.users.factories import UserFactory

# Local
from ..consumers import ChatConsumer
from ..factories import MemberFactory, MessageFactory, RecipientFactory, RoomFactory

pytestmark = pytest.mark.django_db


"""
As workaround for this issue: https://github.com/pytest-dev/pytest-django/issues/580 we are
creating models manually inside the tests as transactions don't appear to work with async.
"""


@database_sync_to_async
def create_message():
    user = UserFactory()
    room = RoomFactory(owner=user)
    message = MessageFactory(room=room, sender=user)
    recipient = RecipientFactory(
        message=message, user=MemberFactory(room=room).user
    ).user
    return message, recipient


@database_sync_to_async
def db_cleanup(message, recipient):
    message.room.delete()
    message.sender.delete()
    recipient.delete()


class TestChatConsumer:
    @pytest.mark.asyncio
    async def test_new_message_as_sender(self):
        message, recipient = await create_message()
        data = {
            "type": "chat.message",
            "group": f"room-{message.room.id}",
            "message": {
                "sender": message.sender.username,
                "text": "test msg",
                "id": message.id,
            },
        }
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/test/ws/",)
        communicator.scope["user"] = message.sender

        await communicator.connect()
        await communicator.send_input(data)

        await communicator.receive_output()
        await communicator.disconnect()
        await db_cleanup(message, recipient)

    @pytest.mark.asyncio
    async def test_new_message_as_recipient(self):
        message, recipient = await create_message()
        data = {
            "type": "chat.message",
            "group": f"room-{message.room.id}",
            "message": {
                "sender": message.sender.username,
                "text": "test msg",
                "id": message.id,
            },
        }
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/test/ws/",)
        communicator.scope["user"] = recipient

        await communicator.connect()
        await communicator.send_input(data)

        await communicator.receive_output()
        await communicator.disconnect()
        await db_cleanup(message, recipient)
