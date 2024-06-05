import base64
from datetime import datetime
from freezegun import freeze_time

from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from landelayo.models import Calendar, Event, Occurrence
from landelayo.enum import Frequency


class CalendarTestCase(APITestCase):
    url = reverse('calendar-list')

    def setUp(self) -> None:
        user = User.objects.create(username='test_user', password='password')
        self.client.force_login(user)

    def test_unique_name(self):
        data = {'name': 'Name'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'name': 'Name'})

        data = {'name': 'Name'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'name': ['This field must be unique.']})
#
#
# class EventTestCase(APITestCase):
#     url = reverse('event-list')
#
#     def data(self, start_date=None, end_date=None, **kwargs) -> dict:
#         return {
#             "title": "Test 1",
#             "description": "Description",
#             "start_date": start_date,
#             "end_date": end_date,
#             "calendar": "Example",
#             "attendees": [self.user.id],
#             **kwargs
#         }
#
#     def setUp(self) -> None:
#         Calendar.objects.create(name='Example')
#         self.user = User.objects.create(username='test_user', password='password', email='test@email.com')
#         self.client.force_login(self.user)
#
#     def test_required_fields(self):
#         data = {}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(
#             response.json(), {
#                 'title': ['This field is required.'],
#                 'description': ['This field is required.'],
#                 'start_date': ['This field is required.'],
#                 'end_date': ['This field is required.'],
#                 'calendar': ['This field is required.'],
#                 'attendees': ['This field is required.']
#             })
#
#     def test_invalid_date_range(self):
#         data = self.data(start_date='2023-01-01T09:00:00+00:00', end_date='2022-12-31T09:00:00+00:00')
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json(), {'non_field_errors': ['Invalid date range']})
#
#     @freeze_time('2023-01-01')
#     def test_past_dates(self):
#         data = self.data(
#             start_date=timezone.make_aware(datetime(2022, 1, 1, 12, 0)),
#             end_date=timezone.make_aware(datetime(2023, 1, 1, 12, 0)),
#         )
#
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json(), {'non_field_errors': ['Invalid date range']})
#
#     @freeze_time('2023-01-01')
#     def test_create_event(self):
#         data = self.data(start_date=datetime(2023, 1, 1, 9), end_date=datetime(2023, 1, 1, 10))
#
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(Event.objects.count(), 1)
#         self.assertEqual(response.json(), {
#             'attendees': [1],
#             'calendar': 'Example',
#             'description': 'Description',
#             'end_date': '2023-01-01T10:00:00Z',
#             'id': 1,
#             'recurrence': None,
#             'start_date': '2023-01-01T09:00:00Z',
#             'title': 'Test 1'
#         })
#
#     def test_update_meeting(self):
#         user_2 = User.objects.create(username='user_2', password='password', email='user_2@email.com')
#         event = Event.objects.create(
#             title='Original',
#             description='Original Description',
#             calendar=Calendar.objects.get(),
#             start_date=timezone.make_aware(datetime(2023, 12, 12, 12)),
#             end_date=timezone.make_aware(datetime(2023, 12, 12, 14)),
#             creator=self.user
#         )
#         event.attendees.add(self.user)
#
#         self.assertEqual(event.title, 'Original')
#         self.assertEqual(event.start_date, timezone.make_aware(datetime(2023, 12, 12, 12)))
#         with freeze_time('2023-01-01'):
#             data = self.data(
#                 start_date=datetime(2023, 1, 1, 9),
#                 end_date=datetime(2023, 1, 1, 10),
#                 attendees=[user_2.id, self.user.id]
#             )
#             url = reverse('event-detail', kwargs={'pk': event.id})
#             response = self.client.patch(url, data, format='json')
#             self.assertEqual(response.status_code, 200)
#
#             event.refresh_from_db()
#             self.assertEqual(event.title, 'Test 1')
#             self.assertEqual(event.description, 'Description')
#             self.assertEqual(event.start_date, timezone.make_aware(datetime(2023, 1, 1, 9)))
#
#
# class RecurrenceTestCase(APITestCase):
#     url = reverse('event-list')
#
#     def data(self, recurrence) -> dict:
#         return {
#             "title": "Test 1",
#             "description": "Description",
#             "start_date": timezone.now() + timezone.timedelta(hours=2),
#             "end_date": timezone.now() + timezone.timedelta(hours=3),
#             "calendar": "Example",
#             "attendees": [self.user.id],
#             'recurrence': recurrence
#         }
#
#     def setUp(self) -> None:
#         Calendar.objects.create(name='Example')
#         self.user = User.objects.create(username='test_user', password='password', email='test@email.com')
#         self.client.force_login(self.user)
#
#     def test_invalid_frequency(self):
#         recurrence = {'frequency': 'Invalid'}
#         data = self.data(recurrence)
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json(), {'recurrence': {'frequency': ['"Invalid" is not a valid choice.']}})
#
#     def test_frequency(self):
#         recurrence = {'frequency': 'DAILY'}
#         data = self.data(recurrence)
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.json()['recurrence'], {'frequency': 'DAILY'})
#
#     def test_invalid_count_until(self):
#         recurrence = {'frequency': 'DAILY', 'count': 5, 'until': '2025-01-01'}
#         data = self.data(recurrence)
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()['recurrence'], {'non_field_errors': ['Invalid count and until combination']})
#
#     def test_invalid_date(self):
#         recurrence = {'frequency': 'DAILY', 'count': 5, 'until': '2023-01-01'}
#         data = self.data(recurrence)
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()['recurrence'], {'until': ['Date cannot be in the past.']})
#
#     def test_invalid_period_rule(self):
#         recurrence = {
#             'frequency': 'DAILY', 'count': 5, 'until': '2025-01-01',
#             'period': {'rule': 'Invalid', 'sequence': [0, 1]}
#         }
#         data = self.data(recurrence)
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()['recurrence']['period'], {'rule': ['"Invalid" is not a valid choice.']})
#
#     def test_recurrence(self):
#         recurrence = {
#             'frequency': 'WEEKLY', 'count': 5,
#             'period': {'rule': 'BY_WEEK_DAY', 'sequence': [0, 1]}
#         }
#         data = self.data(recurrence)
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.json()['recurrence'], {
#             'frequency': 'WEEKLY', 'count': 5,
#             'period': {'rule': 'BY_WEEK_DAY', 'sequence': [0, 1]}
#         })
#
#
# class UpcomingTestCase(APITestCase):
#     url = reverse('upcoming-list')
#
#     def setUp(self):
#         self.maxDiff = None
#         cal = Calendar.objects.create(name='Example')
#         user = User.objects.create(username='test_user', password='password')
#         self.event = Event.objects.create(
#             start_date=timezone.make_aware(datetime(2024, 1, 1, 12, 0)),
#             end_date=timezone.make_aware(datetime(2024, 1, 1, 13, 0)),
#             title='1st Event',
#             description='This is what we do',
#             calendar=cal,
#             creator=user,
#             recurrence={
#                 'frequency': 'DAILY', 'count': 5,
#                 'period': {'rule': 'BY_WEEK_DAY', 'sequence': [0, 1]}
#             }
#         )
#         self.event_2 = Event.objects.create(
#             start_date=timezone.make_aware(datetime(2024, 1, 4, 16, 0)),
#             end_date=timezone.make_aware(datetime(2024, 1, 4, 17, 30)),
#             title='2nd Event',
#             description='Description Here',
#             calendar=cal,
#             creator=user,
#             recurrence={
#                 'frequency': 'WEEKLY',
#                 'period': {'rule': 'BY_WEEK_DAY', 'sequence': [3, 4]}
#             }
#         )
#         self.event.attendees.add(user)
#         self.client.force_login(user)
#
#     def test_invalid_period(self):
#         data = {'period': 'INVALID', 'from_date': '2024-01-01', 'to_date': '2024-01-03'}
#         response = self.client.get(self.url, data=data)
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json(), {'period': ['"INVALID" is not a valid choice.']})
#
#     def test_custom_no_date(self):
#         data = {'period': 'CUSTOM', 'from_date': '2024-01-01'}
#         response = self.client.get(self.url, data=data)
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json(), {'period': ['dates required']})
#
#     def test_custom_date_range(self):
#         data = {'period': 'CUSTOM', 'from_date': '2024-01-01', 'to_date': '2023-12-01'}
#         response = self.client.get(self.url, data=data)
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json(), {'period': ['Invalid date range']})
#
#
#     def test_custom_date_single_event(self):
#         data = {'period': 'CUSTOM', 'from_date': '2024-01-01', 'to_date': '2024-01-03'}
#         response = self.client.get(self.url, data=data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 2)
#         self.assertEqual(response.json(), [
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-01T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-01T12:00:00Z',
#                 'temp_id': 1,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-02T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-02T12:00:00Z',
#                 'temp_id': 2,
#                 'title': '1st Event'
#             }
#         ])
#
#     def test_custom_multiple_events(self):
#         data = {'period': 'CUSTOM', 'from_date': '2024-01-01', 'to_date': '2024-01-06'}
#         response = self.client.get(self.url, data=data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 4)
#         self.assertEqual(response.json(), [
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-01T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-01T12:00:00Z',
#                 'temp_id': 1,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-02T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-02T12:00:00Z',
#                 'temp_id': 2,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-04T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-04T16:00:00Z',
#                 'temp_id': 3,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-05T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-05T16:00:00Z',
#                 'temp_id': 4,
#                 'title': '2nd Event'
#             }
#         ])
#
#     def test_custom_long(self):
#         data = {'period': 'CUSTOM', 'from_date': '2024-03-11', 'to_date': '2024-03-16'}
#         response = self.client.get(self.url, data=data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 2)
#         self.assertEqual(response.json(), [
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-03-14T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-03-14T16:00:00Z',
#                 'temp_id': 1,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-03-15T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-03-15T16:00:00Z',
#                 'temp_id': 2,
#                 'title': '2nd Event'
#             }
#         ])
#
#     @freeze_time('2024-01-01')
#     def test_filter_day(self):
#         data = {'period': 'DAY'}
#         response = self.client.get(self.url, data=data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 1)
#         self.assertEqual(response.json(), [
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-01T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-01T12:00:00Z',
#                 'temp_id': 1,
#                 'title': '1st Event'
#             },
#
#         ])
#
#     @freeze_time('2024-01-01')
#     def test_filter_week(self):
#         # 2023-12-31 to 2024-01-06
#         data = {'period': 'WEEK'}
#         response = self.client.get(self.url, data=data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 4)
#         self.assertEqual(response.json(), [
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-01T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-01T12:00:00Z',
#                 'temp_id': 1,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-02T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-02T12:00:00Z',
#                 'temp_id': 2,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-04T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-04T16:00:00Z',
#                 'temp_id': 3,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-05T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-05T16:00:00Z',
#                 'temp_id': 4,
#                 'title': '2nd Event'
#             }
#         ])
#
#     @freeze_time('2024-01-01')
#     def test_filter_month(self):
#         data = {'period': 'MONTH'}
#         response = self.client.get(self.url, data=data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 13)
#         self.assertEqual(response.json(), [
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-01T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-01T12:00:00Z',
#                 'temp_id': 1,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-02T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-02T12:00:00Z',
#                 'temp_id': 2,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-08T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-08T12:00:00Z',
#                 'temp_id': 3,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-09T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-09T12:00:00Z',
#                 'temp_id': 4,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'This is what we do',
#                 'end_date': '2024-01-15T13:00:00Z',
#                 'event': self.event.id,
#                 'id': None,
#                 'start_date': '2024-01-15T12:00:00Z',
#                 'temp_id': 5,
#                 'title': '1st Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-04T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-04T16:00:00Z',
#                 'temp_id': 6,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-05T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-05T16:00:00Z',
#                 'temp_id': 7,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-11T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-11T16:00:00Z',
#                 'temp_id': 8,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-12T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-12T16:00:00Z',
#                 'temp_id': 9,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-18T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-18T16:00:00Z',
#                 'temp_id': 10,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-19T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-19T16:00:00Z',
#                 'temp_id': 11,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-25T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-25T16:00:00Z',
#                 'temp_id': 12,
#                 'title': '2nd Event'
#             },
#             {
#                 'calendar': 'Example',
#                 'cancelled': False,
#                 'description': 'Description Here',
#                 'end_date': '2024-01-26T17:30:00Z',
#                 'event': self.event_2.id,
#                 'id': None,
#                 'start_date': '2024-01-26T16:00:00Z',
#                 'temp_id': 13,
#                 'title': '2nd Event'
#             },
#
#         ])


class OccurrenceTestCase(APITestCase):

    @staticmethod
    def url(pk):
        return reverse('event-occurrence', kwargs={'pk': pk})

    def unique_key(self, start_date, end_date):
        char = f'{self.event.id}_{start_date}_{end_date}'
        return base64.urlsafe_b64encode(char.encode()).decode()

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.upcoming_url = reverse('upcoming-list')
        self.cal = Calendar.objects.create(name='Example')
        user = User.objects.create(username='test_user', password='password')
        self.client.force_login(user)
        self.event = Event.objects.create(
            start_date=timezone.make_aware(datetime(2024, 1, 1, 12, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 1, 13, 0)),
            title='1st Event',
            description='This is what we do',
            calendar=self.cal,
            creator=user,
            recurrence={
                'frequency': 'DAILY', 'count': 5
            }
        )

    @freeze_time('2024-01-01')
    def test_cancel_occurrence(self):
        start = timezone.make_aware(datetime(2024, 1, 2, 12, 0))
        end = timezone.make_aware(datetime(2024, 1, 2, 13, 0))
        data = {
            'title': 'Update Title',
            'description': 'Update description',
            'start_date': start,
            'end_date': end,
            'occurrence_key': self.unique_key(start, end),
            'calendar': self.cal.name,
            'cancelled': True
        }
        response = self.client.put(self.url(self.event.id), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Occurrence.objects.count(), 1)
        self.assertEqual(response.json()['cancelled'], True)

        # check that the saved cancelled occurrence replaces the generated occurrence
        data = {'period': 'CUSTOM', 'from_date': '2024-01-01', 'to_date': '2024-01-02'}
        response = self.client.get(self.upcoming_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[1]['cancelled'], True)

    @freeze_time('2024-01-03')
    def test_edit_occurrence(self):
        start = timezone.make_aware(datetime(2024, 1, 3, 12, 0))
        end = timezone.make_aware(datetime(2024, 1, 3, 13, 0))
        data = {'period': 'DAY'}
        response = self.client.get(self.upcoming_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json(), [{
            'id': None,
            'event': self.event.id,
            'unique_key': self.unique_key(start, end),
            'title': '1st Event',
            'description': 'This is what we do',
            'calendar': self.cal.name,
            'start_date': '2024-01-03T12:00:00Z',
            'end_date': '2024-01-03T13:00:00Z',
            'cancelled': False
        }])

        # update this occurrence
        new_start = timezone.make_aware(datetime(2024, 1, 3, 12, 30)),
        data = {
            'title': 'Update Title',
            'description': 'Update description',
            'start_date': new_start,
            'end_date': end,
            'occurrence_key': self.unique_key(start, end),
            'calendar': self.cal.name
        }
        response = self.client.put(self.url(self.event.id), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Occurrence.objects.count(), 1)
        self.assertEqual(response.json(), {
            'id': 1,
            'event': 1,
            'title': 'Update Title',
            'description': 'Update description',
            'start_date': '2024-01-03T12:30:00Z',
            'end_date': '2024-01-03T13:00:00Z',
            'unique_key': self.unique_key(start, end),
            'calendar': self.cal.name,
            'cancelled': False
        })

        # check edited occurrence replaces generated occurrance
        occ_1_start = timezone.make_aware(datetime(2024, 1, 1, 12, 0))
        occ_1_end = timezone.make_aware(datetime(2024, 1, 1, 13, 0))
        occ_2_start = timezone.make_aware(datetime(2024, 1, 2, 12, 0))
        occ_2_end = timezone.make_aware(datetime(2024, 1, 2, 13, 0))
        occ_3_start = timezone.make_aware(datetime(2024, 1, 3, 12, 0))
        occ_3_end = timezone.make_aware(datetime(2024, 1, 3, 13, 0))

        data = {'period': 'CUSTOM', 'from_date': '2024-01-01', 'to_date': '2024-01-03'}
        response = self.client.get(self.upcoming_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(response.json(), [
            {
                'id': None,
                'event': 1,
                'title': '1st Event',
                'description': 'This is what we do',
                'calendar': self.cal.name,
                'cancelled': False,
                'unique_key': self.unique_key(occ_1_start, occ_1_end),
                'start_date': '2024-01-01T12:00:00Z',
                'end_date': '2024-01-01T13:00:00Z'
            },
            {
                'id': None,
                'event': 1,
                'title': '1st Event',
                'description': 'This is what we do',
                'calendar': self.cal.name,
                'cancelled': False,
                'unique_key': self.unique_key(occ_2_start, occ_2_end),
                'start_date': '2024-01-02T12:00:00Z',
                'end_date': '2024-01-02T13:00:00Z'
            },
            {
                'id': 1,
                'event': 1,
                'title': 'Update Title',
                'description': 'Update description',
                'calendar': self.cal.name,
                'cancelled': False,
                'unique_key': self.unique_key(occ_3_start, occ_3_end),
                'start_date': '2024-01-03T12:30:00Z',
                'end_date': '2024-01-03T13:00:00Z'
            }
        ])
