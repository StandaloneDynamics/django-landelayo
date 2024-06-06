from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from landelayo.models import Calendar, Event
from landelayo.serializers import CalendarSerializer, EventSerializer, ParamSerializer, OccurrenceSerializer
from landelayo.utils import RequestParams
from landelayo.occurrences import upcoming_occurrences


class CalendarViewSet(viewsets.ModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(creator=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(creator=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['PUT'], detail=True, serializer_class=OccurrenceSerializer)
    def occurrence(self, request, pk, **kwargs):
        """
        Update an events occurrence
        """
        event = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'event': event})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpcomingViewSet(viewsets.GenericViewSet):
    serializer_class = OccurrenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(
            Q(attendees=self.request.user) | Q(creator=self.request.user)
        ).select_related('calendar')

    @extend_schema(
        parameters=[
            ParamSerializer
        ]
    )
    def list(self, *args, **kwargs):
        serializer = ParamSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        p = serializer.validated_data
        params = RequestParams(
            period=p['period'],
            calendar=p.get('calendar'),
            from_date=p.get('from_date'),
            to_date=p.get('to_date')
        )
        occurrences = upcoming_occurrences(params, self.get_queryset())
        return Response(self.get_serializer(occurrences, many=True).data, status=status.HTTP_200_OK)
