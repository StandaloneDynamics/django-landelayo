from typing import Optional, List
from datetime import date
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext, gettext_lazy as _
from django.conf import settings
from django_enumfield import enum
from datetime import datetime
from dateutil.rrule import rrule

from .enum import Frequency, Period


class Calendar(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='event_attendees')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_creator')
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    recurrence = models.JSONField(null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}: {self.start_date}'

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def get_rule(self) -> dict:
        # convert the date rules do dictionary
        kwargs = {'freq': Frequency[self.recurrence['frequency']].to_rrule()}
        if 'count' in self.recurrence:
            kwargs['count'] = self.recurrence['count']

        if 'interval' in self.recurrence:
            kwargs['interval'] = self.recurrence['interval']
        if 'until' in self.recurrence:
            kwargs['until'] = self.recurrence['until']

        if 'period' in self.recurrence:
            rule = Period[self.recurrence['period']['rule']].to_rrule()
            sequence = self.recurrence['period']['sequence']
            kwargs[rule] = sequence

        return kwargs

    def is_occurrence_saved(self, start, end):
        """
        :param datetime start:
        :param datetime end:
        :rtype: Occurrence

        """
        saved: Occurrence
        for saved in self.saved_occurrences:
            if saved.original_start_date == start and saved.original_end_date == end:
                return saved
        return None

    def create_occurrence(self, start_date, end_date=None):
        """
        :param datetime start_date:
        :param datetime end_date:
        :rtype: Occurrence
        """
        if end_date is None:
            end_date = start_date + (self.end_date - self.start_date)

        saved_occurrence = self.is_occurrence_saved(start_date, end_date)
        if saved_occurrence:
            return saved_occurrence

        return Occurrence(
            event=self,
            title=self.title,
            description=self.description,
            start_date=start_date,
            end_date=end_date,
            original_start_date=start_date,
            original_end_date=end_date

        )

    def occurrence_between(self, start_date: datetime, end_date: datetime):
        """
        :rtype: List[Occurrence]
        """
        self.saved_occurrences = self.occurrences.all()
        occurrences = []
        if self.recurrence is None:
            if self.start_date < end_date and self.end_date > start_date:
                return [self.create_occurrence(self.start_date)]
            else:
                return []
        else:
            if self.start_date > end_date:
                return []
            if 'until' in self.recurrence:
                if self.recurrence['until'] < start_date.date():
                    return []

            rules = self.get_rule()
            for ocurr in list(rrule(dtstart=self.start_date, until=end_date, **rules)):
                if start_date <= ocurr <= end_date:
                    occurrences.append(self.create_occurrence(ocurr))
            return occurrences


class Occurrence(models.Model):
    event = models.ForeignKey(Event, related_name='occurrences', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    cancelled = models.BooleanField(default=False)
    original_start_date = models.DateTimeField()
    original_end_date = models.DateTimeField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.title}: {self.start_date} - {self.end_date}'

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
