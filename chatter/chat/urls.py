# Django
from django.urls import path

# Local
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.do_redirect, name="do_redirect"),
    path("~new/", views.create_room, name="create_room"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
]
