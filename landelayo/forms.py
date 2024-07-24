from django import forms
from landelayo.models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('content_type', 'object_id')
