from rest_framework import routers

from landelayo.views import CalendarViewSet, EventViewSet, UpcomingViewSet

router = routers.DefaultRouter()
router.register(r'calendars', CalendarViewSet, basename='calendar')
router.register(r'events', EventViewSet, basename='event')
router.register(r'upcoming', UpcomingViewSet, basename='upcoming')
