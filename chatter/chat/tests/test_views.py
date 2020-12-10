# Django
from django.http import Http404
from django.urls import reverse

# Third Party Libraries
import pytest

# Local
from .. import views
from ..factories import RecipientFactory, RoomFactory
from ..models import Message, Room

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


class TestCreateRoom:
    def test_get(self, rf, user):
        req = rf.get(reverse("chat:create_room"))
        req.user = user
        assert views.create_room(req).status_code == 200

    def test_post(self, rf, user):
        req = rf.post(reverse("chat:create_room"), {"name": "test-room"})
        req.user = user
        resp = views.create_room(req)
        room = Room.objects.get()
        assert resp.url == room.get_absolute_url()
        assert room.owner == user


class TestSendMessage:
    def test_send_no_text(self, rf, room):
        req = rf.post(reverse("chat:send_message", args=[room.id]), {"text": ""})
        req.user = room.owner
        resp = views.send_message(req, room.id)
        assert resp.status_code == 400
        assert Message.objects.count() == 0

    def test_send(self, rf, room, mocker):
        mocker.Mock("asgiref.sync.async_to_sync")
        req = rf.post(reverse("chat:send_message", args=[room.id]), {"text": "hello"})
        req.user = room.owner
        resp = views.send_message(req, room.id)
        assert resp.status_code == 200

        msg = Message.objects.first()
        assert msg.sender == req.user
        assert msg.text == "hello"
        assert msg.room == room


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
