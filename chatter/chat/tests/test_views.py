# Third Party Libraries
# Django
from django.http import Http404
from django.urls import reverse

import pytest

# Local
from .. import views
from ..factories import RecipientFactory, RoomFactory

pytestmark = pytest.mark.django_db


class TestRoomDetail:
    def test_user_not_member(self, rf, user):
        room = RoomFactory()
        req = rf.get(room.get_absolute_url())
        req.user = user
        with pytest.raises(Http404):
            views.room_detail(req, room.id)

    def test_user_is_member(self, rf, room):
        req = rf.get(room.get_absolute_url())
        req.user = room.owner
        resp = views.room_detail(req, room.id)
        assert resp.status_code == 200


class TestDoRedirect:
    def test_user_has_no_rooms(self, rf, user):
        req = rf.get("/")
        req.user = user

        resp = views.do_redirect(req)
        assert resp.url == reverse("chat:create_room")

    def test_user_has_room(self, rf, room):
        req = rf.get("/")
        req.user = room.owner

        resp = views.do_redirect(req)
        assert resp.url == room.get_absolute_url()

    def test_user_has_sent_message(self, rf, message):

        RoomFactory(owner=message.sender)

        req = rf.get("/")
        req.user = message.sender

        resp = views.do_redirect(req)
        assert resp.url == message.room.get_absolute_url()

    def test_user_has_received_message(self, rf, message):

        user = RecipientFactory(message=message).user

        RoomFactory(owner=user)

        req = rf.get("/")
        req.user = user

        resp = views.do_redirect(req)
        assert resp.url == message.room.get_absolute_url()
