# Django
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

# Third Party Libraries
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Chatter
from chatter.common.turbo.response import TurboStreamTemplateResponse

# Local
from .forms import RoomForm
from .models import Message, Recipient, Room

MAX_NUM_MESSAGES = 9


@login_required
def do_redirect(request):
    """
    If no rooms, then jumps to the "create room" page. Otherwise jumps
    to the most recently updated room the user belongs to.
    """
    recipient = (
        Recipient.objects.filter(user=request.user, read__isnull=True)
        .select_related("message__room")
        .order_by("-created")
        .first()
    )
    if recipient:
        return redirect(recipient.message.room)

    message = (
        Message.objects.filter(sender=request.user)
        .select_related("room")
        .order_by("-created")
        .first()
    )
    if message:
        return redirect(message.room)

    room = Room.objects.for_user(request.user).order_by("name").first()

    if room:
        return redirect(room)

    return redirect("chat:create_room")


@login_required
def search(request):
    search = request.GET.get("q", "").strip()
    if search:
        messages = Message.objects.filter(text__icontains=search).order_by(
            "room_id", "-created"
        )
    else:
        messages = Message.objects.none()
    return TemplateResponse(
        request, "chat/search.html", {"search": search, "chat_messages": messages}
    )


@login_required
def room_detail(request, room_id):
    """Shows the room with all messages. For now show all messages,
    but we probably want to just show last 20 or so by default.
    """
    room = get_object_or_404(
        Room.objects.for_user(request.user).select_related("owner"), pk=room_id
    )
    messages = (
        Message.objects.filter(room=room).order_by("-created").select_related("sender")
    )

    room.mark_read(request.user)

    return TemplateResponse(
        request,
        "chat/room.html",
        {"room": room, "chat_messages": messages, "page_size": MAX_NUM_MESSAGES},
    )


@login_required
@require_POST
def send_message(request, room_id):
    room = get_object_or_404(Room.objects.for_user(request.user), pk=room_id)
    text = request.POST.get("text")
    if not text:
        return HttpResponseBadRequest("Invalid message")
    message = room.create_message(request.user, text)
    data = {
        "type": "chat.message",
        "group": f"room-{room.id}",
        "message": {"sender": request.user.username, "text": text, "id": message.id},
    }
    async_to_sync(get_channel_layer().group_send)("chat", data)
    return JsonResponse(data)


@login_required
def create_room(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.save()
            return redirect(room)
        return TurboStreamTemplateResponse(
            "chat/_room_form.html", {"form": form}, action="update", target="room-form"
        )
    else:
        form = RoomForm()
    return TemplateResponse(request, "chat/room_form.html", {"form": form})
