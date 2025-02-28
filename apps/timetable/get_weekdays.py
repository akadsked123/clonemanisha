from apps.timetable.models import Weekday

def get_ordered_weekdays():
    return Weekday.objects.all().order_by('day_id')