# Django
from django.urls import path

# Local
from . import views

app_name = "chat"

urlpatterns = [
    path("~new/", views.create_room, name="create_room"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
    path("<int:room_id>/~send/", views.send_message, name="send_message"),
    path("<int:room_id>/messages/", views.latest_messages, name="latest_messages"),
    path("search/", views.search, name="search"),
    path("sidebar/", views.sidebar, name="sidebar"),
]
