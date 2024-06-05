from django.contrib import admin

from landelayo.models import Calendar

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('name', )
