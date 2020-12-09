# Standard Library
import re

# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction

# Third Party Libraries
from model_utils.models import TimeStampedModel

MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>!.?[\]|{}]+)")


class RoomManager(models.Manager):
    @transaction.atomic()
    def create_message(self, sender, text):

        message = self.message_set.create(sender=sender, text=text)
        members = [m for m in list(self.members.all()) + [self.owner] if m != sender]

        mentions = MENTIONS_RE.findall(text)

        Recipient.objects.bulk_create(
            [
                Recipient(
                    message=message, user=member, mentioned=member.username in mentions
                )
                for member in members
            ]
        )

        # if anyone @mentioned, automatically add them to the chatroom
        member_usernames = [m.username for m in members]
        usernames = [
            username
            for username in mentions
            if username not in member_usernames and username != sender.username
        ]

        new_members = Member.objects.bulk_create(
            [
                Member(room=self, user=user)
                for user in get_user_model().filter(username__in=usernames)
            ]
        )

        Recipient.objects.bulk_create(
            [
                Recipient(message=message, user=member.user, mentioned=True)
                for member in new_members
            ]
        )
        return message


class Room(TimeStampedModel):
    name = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rooms_owned"
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Member",
        blank=True,
        related_name="rooms_joined",
    )

    def __str__(self):
        return self.name


class Member(TimeStampedModel):
    """Any rooms the user is a (non-owner) member of.
    You can add any user by just doing "@username" in a message.
    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Message(TimeStampedModel):
    text = models.TextField()

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent"
    )

    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Recipient", related_name="messages_received",
    )


class Recipient(TimeStampedModel):
    """Indicates that message has been read by this user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    mentioned = models.BooleanField(default=False)
    read = models.DateTimeField(null=True, blank=True)
