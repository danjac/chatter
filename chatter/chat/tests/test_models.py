# Third Party Libraries
import pytest

# Chatter
from chatter.users.factories import UserFactory

# Local
from ..factories import MemberFactory

pytestmark = pytest.mark.django_db


class TestRoomModel:
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
