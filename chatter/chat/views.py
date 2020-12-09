# Django
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

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


@login_required
def unread_messages(request):
    """Show all messages in rooms I have not read yet."""
    recipients = (
        Recipient.objects.filter(user=request.user, read__isnull=True)
        .select_related("message", "message__room")
        .order_by("-created")
    )
    return TemplateResponse(
        request, "chat/unread_messages.html", {"message_recipients": recipients}
    )


@login_required
def sidenav(request):
    """Refreshes sidenav with latest messages and status"""
    # - all rooms I belong to
    # - rooms I have been @mentioned
    # - new (unread) messages are flagged
    messages = Message.objects.order_by("-created")
    return TemplateResponse(request, "chat/_sidenav.html", {"chat_messages": messages})


@login_required
@require_POST
def send_message(request, room_id):
    """Sends a new message."""
    room = get_object_or_404(Room.objects.select_related("owner"), pk=room_id)

    if not room.is_member(request.user):
        raise PermissionDenied("You must be a member to post a message in this room")

    text = request.POST.get("text", None)
    if not text:
        return HttpResponseBadRequest("No message text provided")

    room.create_message(request.user, text)
    # send socket event
    return redirect(f"{room.get_absolute_url()}#send-message")
