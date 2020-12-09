# Django
from django import template

# Local
from ..models import Room

register = template.Library()


@register.simple_tag(takes_context=True)
def get_rooms(context):
    return Room.objects.all()
