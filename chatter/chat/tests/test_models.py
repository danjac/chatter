# Third Party Libraries
import pytest

# Chatter
from chatter.users.factories import UserFactory

# Local
from ..factories import MemberFactory, MessageFactory
from ..models import Message, Room

pytestmark = pytest.mark.django_db


class TestRoomManager:
    def test_for_user(self, room, anonymous_user):
        assert Room.objects.for_user(anonymous_user).count() == 0
        assert Room.objects.for_user(UserFactory()).count() == 0
        assert Room.objects.for_user(room.owner).count() == 1
        assert Room.objects.for_user(MemberFactory(room=room).user).count() == 1


class TestRoomModel:
    def test_is_member(self, room, anonymous_user):
        member = MemberFactory(room=room).user
        non_member = UserFactory()

        assert not room.is_member(anonymous_user)
        assert not room.is_member(non_member)
        assert room.is_member(member)
        assert room.is_member(room.owner)

    def test_create_message(self, room):
        member = MemberFactory(room=room).user
        mentioned = UserFactory(username="rando")

        message = room.create_message(room.owner, "hello, @rando")
        assert message.sender == room.owner

        recipients = message.recipients.all()

        assert recipients.count() == 2
        assert mentioned in recipients
        assert member in recipients
        assert room.owner not in recipients

        members = room.members.all()

        assert members.count() == 2
        assert mentioned in members
        assert member in members
        assert room.owner not in members


class TestMessageManager:
    def test_for_user(self, room, anonymous_user):
        message = MessageFactory(room=room)

        assert Message.objects.for_user(anonymous_user).count() == 0
        assert Message.objects.for_user(UserFactory()).count() == 0
        assert Message.objects.for_user(message.room.owner).count() == 1
        assert (
            Message.objects.for_user(MemberFactory(room=message.room).user).count() == 1
        )
