# Standard Library
import re

# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse

# Third Party Libraries
from model_utils.models import TimeStampedModel

MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>!.?[\]|{}]+)")


class RoomQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_anonymous:
            return self.none()
        return self.filter(models.Q(owner=user) | models.Q(members=user)).distinct()


class RoomManager(models.Manager.from_queryset(RoomQuerySet)):
    ...


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

    objects = RoomManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("chat:room_detail", args=[self.id])

    def is_member(self, user):
        if user.is_anonymous:
            return False
        return self.owner == user or self.members.filter(pk=user.id).exists()

    @transaction.atomic()
    def create_message(self, sender, text):
        """Creates a new message. Automatically adds recipient instances
        for all members/owner other than sender, as well as any users @mentioned
        in the message text."""

        message = self.message_set.create(sender=sender, text=text)
        members = [m for m in list(self.members.all()) + [self.owner] if m != sender]

        mentions = MENTIONS_RE.findall(text)

        # we should be careful if anyone has username "channel" or "here"...
        everyone = "channel" in mentions or "here" in mentions

        Recipient.objects.bulk_create(
            [
                Recipient(
                    message=message,
                    user=member,
                    mentioned=everyone or member.username in mentions,
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
                for user in get_user_model().objects.matches_usernames(usernames)
            ]
        )

        Recipient.objects.bulk_create(
            [
                Recipient(message=message, user=member.user, mentioned=True)
                for member in new_members
            ]
        )
        return message


class Member(TimeStampedModel):
    """Any rooms the user is a (non-owner) member of.
    You can add any user by just doing "@username" in a message.
    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class MessageQuerySet(models.QuerySet):
    def for_user(self, user):
        """Return only messages for rooms the user belongs to"""

        if user.is_anonymous:
            return self.none()
        return self.filter(
            models.Q(room__owner=user) | models.Q(room__members=user)
        ).distinct()


class MessageManager(models.Manager.from_queryset(MessageQuerySet)):
    ...


class Message(TimeStampedModel):
    text = models.TextField()

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent"
    )

    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Recipient", related_name="messages_received",
    )

    objects = MessageManager()


class Recipient(TimeStampedModel):
    """Indicates that message has been read by this user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    mentioned = models.BooleanField(default=False)
    read = models.DateTimeField(null=True, blank=True)
    # TBD: unique constraint for message/user
