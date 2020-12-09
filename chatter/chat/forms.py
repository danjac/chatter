# Django
from django import forms

# Local
from .models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("name",)
