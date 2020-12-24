# Django
from django.utils import timezone

# Third Party Libraries
import pytest

# Local
from ..factories import MemberFactory, MessageFactory, RecipientFactory, RoomFactory
from ..templatetags.chat import get_rooms

pytestmark = pytest.mark.django_db


class TestGetRooms:
    def test_get_rooms(self, user):
        own_room = RoomFactory(owner=user)
        member_room = MemberFactory(user=user).room
        new_message_room = RoomFactory(owner=user)
        mentioned_message_room = RoomFactory(owner=user)
        old_message_room = RoomFactory(owner=user)
        new_message_sender_room = MemberFactory(user=user).room

        MessageFactory(room=new_message_sender_room, sender=user)
        RecipientFactory(
            message=MessageFactory(room=old_message_room),
            user=user,
            read=timezone.now(),
        )
        new = RecipientFactory(
            message=MessageFactory(room=new_message_room), user=user, read=None
        )
        mentioned = RecipientFactory(
            message=MessageFactory(room=mentioned_message_room),
            user=user,
            mentioned=True,
            read=None,
        )

        rooms = get_rooms(user)

        assert {
            "id": mentioned_message_room.id,
            "url": mentioned_message_room.get_absolute_url(),
            "name": mentioned_message_room.name,
            "last_updated": mentioned.created,
            "is_mention": True,
        } in rooms["new"]

        assert {
            "id": new_message_room.id,
            "url": new_message_room.get_absolute_url(),
            "name": new_message_room.name,
            "last_updated": new.created,
            "is_mention": False,
        } in rooms["new"]

        assert {
            "id": own_room.id,
            "name": own_room.name,
            "url": own_room.get_absolute_url(),
            "is_mention": False,
        } in rooms["other"]

        assert {
            "id": member_room.id,
            "name": member_room.name,
            "url": member_room.get_absolute_url(),
            "is_mention": False,
        } in rooms["other"]

        assert {
            "id": new_message_sender_room.id,
            "name": new_message_sender_room.name,
            "url": new_message_sender_room.get_absolute_url(),
            "is_mention": False,
        } in rooms["other"]
