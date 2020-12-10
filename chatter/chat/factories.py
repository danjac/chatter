# Third Party Libraries
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

# Chatter
from chatter.users.factories import UserFactory

# Local
from .models import Member, Message, Recipient, Room


class RoomFactory(DjangoModelFactory):
    name = Faker("slug")
    owner = SubFactory(UserFactory)

    class Meta:
        model = Room


class MemberFactory(DjangoModelFactory):
    room = SubFactory(RoomFactory)
    user = SubFactory(UserFactory)

    class Meta:
        model = Member


class MessageFactory(DjangoModelFactory):
    room = SubFactory(RoomFactory)
    sender = SubFactory(UserFactory)
    text = Faker("text")

    class Meta:
        model = Message


class RecipientFactory(DjangoModelFactory):
    message = SubFactory(MessageFactory)
    user = SubFactory(UserFactory)

    class Meta:
        model = Recipient
