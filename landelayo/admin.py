from django.contrib import admin

from landelayo.models import Calendar, Event
from landelayo.forms import EventForm


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'start_date', 'end_date')
    form = EventForm
