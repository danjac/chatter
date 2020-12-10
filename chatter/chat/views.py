# Django
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

# Third Party Libraries
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Local
from .forms import RoomForm
from .models import Message, Recipient, Room
from .templatetags.chat import get_sidebar


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
        messages = Message.objects.filter(text__icontains=search).order_by("-created")
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
def fetch_latest_messages(request, room_id):
    room = get_object_or_404(
        Room.objects.for_user(request.user).select_related("owner"), pk=room_id
    )
    Recipient.objects.filter(user=request.user, message__room=room).update(
        read=timezone.now()
    )
    messages = (
        Message.objects.filter(room=room)
        .order_by("-created")
        .select_related("sender")[:9]
    )
    return TemplateResponse(request, "chat/_messages.html", {"chat_messages": messages})


@login_required
def sidebar(request):
    return TemplateResponse(
        request, "chat/_sidebar.html", {"rooms": get_sidebar(request.user)}
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
    print("done")
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
    else:
        form = RoomForm()
    return TemplateResponse(request, "chat/room_form.html", {"form": form})
