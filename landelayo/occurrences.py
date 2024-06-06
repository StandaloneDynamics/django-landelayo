from landelayo.utils import period_days


def upcoming_occurrences(params, query):
    """
    :type query: QuerySet
    :type params: RequestParams
    :return: List[Occurrence]
    """
    occur_list = []
    if params.calendar:
        query = query.filter(calendar__name=params.calendar.name)
    dates = period_days(params)

    for event in query:
        occur = event.occurrence_between(dates.from_date, dates.to_date)
        for o in occur:
            occur_list.append(o)
    return occur_list
