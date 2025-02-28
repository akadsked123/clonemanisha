from apps.timetable.models import Periods

def get_ordered_periods():
    periods = Periods.objects.all().order_by('start_time')
    formatted_periods = []
    for index, period in enumerate(periods):
        formatted_periods.append(period.start_time.strftime('%I:%M %p'))
    return formatted_periods