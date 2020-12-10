# Standard Library
import html
import operator

# Django
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

# Third Party Libraries
import bleach
import markdown

# Local
from ..models import Recipient, Room

register = template.Library()


cleaner = bleach.Cleaner(tags=bleach.ALLOWED_TAGS + ["p", "div", "br"], strip=True)


def linkify_callback(attrs, new=False):
    attrs[(None, "target")] = "_blank"
    attrs[(None, "rel")] = "noopener noreferrer nofollow"
    return attrs


@register.filter
@stringfilter
def as_markdown(text):
    try:
        return mark_safe(
            html.unescape(
                bleach.linkify(
                    cleaner.clean(markdown.markdown(text)), [linkify_callback]
                )
            )
            if text
            else ""
        )
    except (ValueError, TypeError):
        return ""


@register.simple_tag
def get_sidebar(user):
    all_recipients = (
        Recipient.objects.filter(user=user, read__isnull=True)
        .select_related("message", "message__sender", "message__room")
        .order_by("-created")
    )

    rooms = Room.objects.for_user(user)

    rv = {"new": [], "other": []}

    for room in rooms:
        recipients = [r for r in all_recipients if r.message.room == room]
        is_mention = bool(recipients and recipients[0].mentioned)

        data = {
            "id": room.id,
            "url": room.get_absolute_url(),
            "name": room.name,
            "is_mention": is_mention,
        }
        if recipients:
            data["last_updated"] = max([r.created for r in recipients])
            rv["new"].append(data)
        else:
            rv["other"].append(data)

    rv["new"].sort(key=operator.itemgetter("last_updated"), reverse=True)
    rv["other"].sort(key=operator.itemgetter("name"))

    return rv
