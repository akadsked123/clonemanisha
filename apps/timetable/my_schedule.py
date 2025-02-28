from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from apps.timetable import get_periods, get_weekdays
from apps.timetable.instructor_conflicts import detect_instructor_conflicts
from apps.timetable.models import GeneratedSchedule, ViewTimetable
from apps.timetable.schedule_instructor import instructor_timetable
from apps.user.utils import get_template_by_user_type

@login_required
def my_schedule(request):
    template = get_template_by_user_type(request.user, 'my-schedule')
    selected_instructor_id = request.user.id
    view_mode = request.GET.get('view', 'table')

    try:
        generated_schedules = GeneratedSchedule.objects.filter(
            institute=request.user.institute,
            result_identification__in=ViewTimetable.objects.filter(
                user=request.user,
                share_to_instructor=True
            ).values('result_identification')
        ).values('result_identification', 'academic_year', 'semester').order_by('-created_at')

        result_identification = request.GET.get('result_identification', None)
        if not result_identification or not GeneratedSchedule.objects.filter(result_identification=result_identification).exists():
            if generated_schedules.exists():
                result_identification = generated_schedules.first()['result_identification']
            else:
                result_identification = None

        if result_identification:
            view_timetable = ViewTimetable.objects.filter(
                user=request.user,
                result_identification=result_identification,
                share_to_instructor=True
            ).first()
            if view_timetable:
                instructor_timetable_data = instructor_timetable(selected_instructor_id, result_identification) if selected_instructor_id else {'instructor_timetable': []}
                conflicts_data = detect_instructor_conflicts(instructor_timetable_data['instructor_timetable'])
            else:
                instructor_timetable_data = {'instructor_timetable': []}
                conflicts_data = {}
        else:
            instructor_timetable_data = {'instructor_timetable': []}
            conflicts_data = {}

    except GeneratedSchedule.DoesNotExist:
        generated_schedules = None
        instructor_timetable_data = {'instructor_timetable': []}
        conflicts_data = {}

    if template and request.user.user_type == 5:
        if "generate_pdf" in request.GET:
          return redirect(reverse('generate_pdf', args=[result_identification, selected_instructor_id]))
        
        return render(request, template, {
            'generated_schedules': generated_schedules,
            **instructor_timetable_data,
            **conflicts_data,
            'days': get_weekdays.get_ordered_weekdays(),
            'periods': get_periods.get_ordered_periods(),
            'view_mode': view_mode,
            'result_identification': result_identification,
            'selected_instructor_id': selected_instructor_id
        })
    return render(request, template, {})