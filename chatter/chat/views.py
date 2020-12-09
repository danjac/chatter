# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone

# Local
from .forms import RoomForm
from .models import Message, Recipient, Room


@login_required
def do_redirect(request):
    """
    If no rooms, then jumps to the "create room" page. Otherwise jumps
    to the most recently updated room the user belongs to.
    """
    room = Room.objects.first()
    if room:
        return redirect(room)
    return redirect("chat:create_room")


@login_required
def room_detail(request, room_id):
    """Shows the room with all messages. For now show all messages,
    but we probably want to just show last 20 or so by default.
    """
    room = get_object_or_404(Room.objects.select_related("owner"), pk=room_id)
    messages = (
        Message.objects.filter(room=room).order_by("-created").select_related("sender")
    )

    Recipient.objects.filter(message__room=room, user=request.user).update(
        read=timezone.now()
    )

    return TemplateResponse(
        request,
        "chat/room.html",
        {
            "room": room,
            "chat_messages": messages,
            "is_member": room.is_member(request.user),
        },
    )


@login_required
def create_room(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.save()
            return redirect(room)
    else:
        form = RoomForm()
    return TemplateResponse(request, "chat/room_form.html", {"form": form})
