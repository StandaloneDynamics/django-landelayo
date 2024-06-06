from dataclasses import dataclass
from datetime import date, datetime, timedelta, time
from django.utils import timezone
from calendar import monthrange

from landelayo.enum import UpcomingPeriod


@dataclass
class DateRange:
    from_date: datetime
    to_date: datetime


@dataclass
class RequestParams:
    period: UpcomingPeriod
    calendar: str = None
    from_date: date = None
    to_date: date = None


def period_days(params: RequestParams) -> DateRange:
    now_date = timezone.now().date()
    if params.period is UpcomingPeriod.DAY:
        from_date = datetime.combine(now_date, time.min)
        to_date = datetime.combine(now_date, time.max)

    elif params.period is UpcomingPeriod.WEEK:
        today = date.today()
        weekday = today.isoweekday()
        start = today - timedelta(days=weekday)
        end = start + timedelta(days=6)
        from_date = datetime.combine(start, time.min)
        to_date = datetime.combine(end, time.max)

    elif params.period is UpcomingPeriod.MONTH:
        _, end = monthrange(now_date.year, now_date.month)
        start = datetime(now_date.year, now_date.month, 1)
        end = datetime(now_date.year, now_date.month, end)

        from_date = datetime.combine(start, time.min)
        to_date = datetime.combine(end, time.max)

    elif params.period is UpcomingPeriod.YEAR:
        start = datetime(now_date.year, 1, 1)
        end = datetime(now_date.year + 1, 1, 1)

        from_date = datetime.combine(start, time.min)
        to_date = datetime.combine(end, time.max)
    else:
        from_date = datetime.combine(params.from_date, time.min)
        to_date = datetime.combine(params.to_date, time.max)

    return DateRange(
        from_date=timezone.make_aware(from_date),
        to_date=timezone.make_aware(to_date)
    )
