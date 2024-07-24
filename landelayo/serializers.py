import base64
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.utils import timezone
from django_enumfield.contrib.drf import NamedEnumField
from landelayo.models import Calendar, Event, Occurrence
from landelayo.enum import Frequency, Period, UpcomingPeriod
from landelayo.settings import get_user_serializer

MINUTE_LENGTH = 60
HOUR_LENGTH = 24
DAY_LENGTH = 7

UserSerializer = get_user_serializer()


class CalendarSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Calendar
        fields = ('id', 'name', 'color', 'created_by')
        read_only_fields = ('id',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'request' in self.context:
            user = self.context["request"].user
            self.validators = [
                UniqueTogetherValidator(
                    queryset=Calendar.objects.filter(created_by=user),
                    fields=["name"],
                    message="Calendar exists for user",
                )
            ]


class PeriodSerializer(serializers.Serializer):
    """
    Week starts on Monday with a value of 0
    Be explicity about the days.
    """
    rule = NamedEnumField(Period, required=True)
    sequence = serializers.ListField(child=serializers.IntegerField(), required=True)


class RecurrenceSerializer(serializers.Serializer):
    frequency = NamedEnumField(Frequency, required=True)
    interval = serializers.IntegerField(required=False)
    count = serializers.IntegerField(required=False)
    until = serializers.DateField(required=False)
    period = PeriodSerializer(required=False)

    def validate_until(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError('Date cannot be in the past.')
        return value

    def validate(self, attrs):
        if attrs.get('count') and attrs.get('until'):
            raise serializers.ValidationError('Invalid count and until combination')

        return attrs


class BasicEventSerializer(serializers.ModelSerializer):
    calendar = CalendarSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'calendar', 'attendees')


class EventSerializer(serializers.ModelSerializer):
    calendar_id = serializers.PrimaryKeyRelatedField(
        queryset=Calendar.objects.all(),
        write_only=True
    )
    calendar = CalendarSerializer(read_only=True)
    recurrence = RecurrenceSerializer(required=False)

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'start_date', 'end_date', 'calendar',
            'attendees', 'recurrence', 'calendar_id'
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if not start_date or not end_date:
            raise serializers.ValidationError('Date fields required')

        if start_date > end_date:
            raise serializers.ValidationError('Invalid date range')

        if start_date < timezone.now():
            raise serializers.ValidationError('Invalid date range')

        return attrs

    def create(self, validated_data):
        calendar = validated_data.pop('calendar_id')
        attendees = validated_data.pop('attendees', None)

        event = Event.objects.create(calendar=calendar, **validated_data)
        if attendees:
            for user in attendees:
                event.attendees.add(user)
        return event

    def update(self, instance, validated_data):
        instance.calendar = validated_data.pop('calendar_id', instance.calendar)
        attendees = validated_data.pop('attendees')
        if attendees:
            instance.attendees.clear()
            for user in attendees:
                instance.attendees.add(user)
        return super().update(instance, validated_data)


class OccurrenceSerializer(serializers.ModelSerializer):
    event = BasicEventSerializer(read_only=True)
    occurrence_id = serializers.IntegerField(write_only=True, required=False)
    occurrence_key = serializers.CharField(write_only=True)
    unique_key = serializers.SerializerMethodField()

    class Meta:
        model = Occurrence
        fields = ('id', 'unique_key', 'event', 'title', 'description',
                  'start_date', 'end_date', 'cancelled', 'occurrence_id', 'occurrence_key')
        read_only_fields = ['id', 'unique_key']

    def get_unique_key(self, obj) -> bytes:
        """
        Occurrences are generated lazily, so they will not have an actual id
        So Generate a constant unique key if occurrence has not being persisted.
        To be used as id when updating an occurrence
        """
        char = f'{obj.event.id}_{obj.original_start_date}_{obj.original_end_date}'
        return base64.urlsafe_b64encode(char.encode())

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError('Invalid date ranges.')
        return attrs

    def create(self, validated_data):
        """
        We need to first check if an occurrence exists in the db by using the occurrence_id field
        as the id. if no occurrence is found assume it's a new object that needs to be saved.
        """
        event = self.context['event']
        occurrence_id = validated_data.get('occurrence_id')
        instance = Occurrence.objects.filter(id=occurrence_id, event=event).first()
        if not instance:
            occurrence_key = validated_data.get('occurrence_key')
            try:
                unique_key = base64.urlsafe_b64decode(occurrence_key).decode()
                event_id, original_start, original_end = unique_key.split('_')
            except ValueError as e:
                raise serializers.ValidationError(e)

            instance = Occurrence(
                original_start_date=original_start, original_end_date=original_end,
                event=event
            )

        instance.title = validated_data.get('title')
        instance.description = validated_data.get('description')
        instance.start_date = validated_data.get('start_date')
        instance.end_date = validated_data.get('end_date')
        instance.cancelled = validated_data.get('cancelled')
        instance.save()

        return instance


class ParamSerializer(serializers.Serializer):
    period = NamedEnumField(UpcomingPeriod, required=True)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    calendar = serializers.SlugRelatedField(
        queryset=Calendar.objects.all(),
        slug_field='name',
        error_messages={'does_not_exist': 'Calendar does not exist'},
        required=False
    )

    def validate_period(self, value):
        period = UpcomingPeriod(value)
        return period

    def validate(self, attrs):
        period = attrs['period']
        if period is UpcomingPeriod.CUSTOM:
            from_date = attrs.get('from_date')
            to_date = attrs.get('to_date')
            if not from_date or not to_date:
                raise serializers.ValidationError({'period': ['dates required']})
            if from_date > to_date:
                raise serializers.ValidationError({'period': ['Invalid date range']})
            # check that date range is at most 1 year to limit results
        return attrs
