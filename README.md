# Landelayo

## Introduction
Landelayo is a set of Django REST API's to manage your calendars, events and their occurrences.

This project was inspired by [django-scheduler](https://pypi.org/project/django-scheduler/) project but with a narrower focus
and a REST API.


## Install And Setup
```commandline
pip install django-landelayo
```
Landelayo uses the `DefaultRouter` provided by the [django rest-framework](https://www.django-rest-framework.org/). 

To incorporate it into your projects `urls.py` file with your other apis, you can do the following
```python
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from landelayo.urls import router as landelayo_router

# Your Main Project Router
router = DefaultRouter()
router.registry.extend(landelayo_router.registry)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    ...
]
```

### Settings
A Configuration variable called `LANDELAYO_USER_SERIALIZER` is available to use your own user serializer.
The default is `landelayo.settings.UserSerializer`


## ViewSets
There are 3 Api's that are provided.
* Calendar 
  * Eg: `http://localhost:8000/api/v1/calendars` 
  * Grouping events.
  * Allows for the creating and editing of different calendar names.
  * [More Documentation and Screenshots Here](docs/calendar/calendar.md)

* Events 
  * Eg: `http://localhost:8000/api/v1/events` 
  * This allows for the creation and editing of events.
  * This also allows for setting the rules for event occurrences.
  * [More Documentation and Screenshots Here](docs/event/event.md)

* Upcoming 
  * Eg: `http://localhost:8000/api/v1/upcoming`
  * View event occurrences over a particular date period (DAY, WEEK, MONTH)
  * The is also an option to view over a custom period (CUSTOM)
  * [More Documentation and Screenshots Here](docs/upcoming/upcoming.md)

## OpenAPI
Landelayo has support for swagger docs
