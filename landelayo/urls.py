from rest_framework import routers

from landelayo.views import CalendarViewSet, EventViewSet, UpcomingViewSet

router = routers.DefaultRouter()
router.register(r'calendar', CalendarViewSet)
router.register(r'event', EventViewSet)
router.register(r'upcoming', UpcomingViewSet, basename='upcoming')
