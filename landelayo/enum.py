from django_enumfield import enum
from dateutil import rrule


class Frequency(enum.Enum):
    YEARLY = 1
    MONTHLY = 2
    WEEKLY = 3
    DAILY = 4
    HOURLY = 5

    __rrule__ = {
        YEARLY: rrule.YEARLY,
        MONTHLY: rrule.MONTHLY,
        WEEKLY: rrule.WEEKLY,
        DAILY: rrule.DAILY,
        HOURLY: rrule.HOURLY
    }

    def to_rrule(self):
        return self.__rrule__[self]


class Period(enum.Enum):
    BY_YEAR_DAY = 1
    BY_MONTH = 2
    BY_MONTH_DAY = 3
    BY_WEEK_NO = 4
    BY_WEEK_DAY = 5
    BY_HOUR = 6

    __rrule__ = {
        BY_YEAR_DAY: 'byyearday',
        BY_MONTH: 'bymonth',
        BY_MONTH_DAY: 'bymonthday',
        BY_WEEK_NO: 'byweekno',
        BY_WEEK_DAY: 'byweekday',
        BY_HOUR: 'byhour',
    }

    def to_rrule(self):
        return self.__rrule__[self]


class UpcomingPeriod(enum.Enum):
    DAY = 1
    WEEK = 2
    MONTH = 3
    YEAR = 4
    CUSTOM = 5


class DaysOfWeek(enum.Enum):
    MO = 1
    TU = 2
    WE = 3
    TH = 4
    FR = 5
    SA = 6
    SU = 7

    __rrules__ = {
        MO: rrule.MO,
        TU: rrule.TU,
        WE: rrule.WE,
        TH: rrule.TH,
        FR: rrule.FR,
        SA: rrule.SA,
        SU: rrule.SU,
    }
