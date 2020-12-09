# Django
from django import template

# Local
from ..models import Recipient, Room

register = template.Library()


@register.simple_tag
def get_sidebar(user):
    recipients = (
        Recipient.objects.filter(user=user, read__isnull=True)
        .select_related("message", "message__sender", "message__room")
        .order_by("-created")
    )

    rooms = Room.objects.for_user(user).order_by("name").distinct()

    rv = []

    for room in rooms:
        recipients = [r for r in recipients if r.message.room == room]
        is_mention = recipients and recipients[0].mentioned

        data = {
            "id": room.id,
            "url": room.get_absolute_url(),
            "name": room.name,
            "is_new": bool(recipients),
            "is_mention": is_mention,
        }
        rv.append(data)
    return rv
