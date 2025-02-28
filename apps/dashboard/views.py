import json
import os
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from apps.curriculum.models import CurriculumYear, Programs
from apps.dashboard.greeting_message_services import GreetingMessage
from apps.institutes.models import Institutes
from apps.timetable import get_periods, get_weekdays
from apps.timetable.item_per_page_utils import validate_items_per_page
from apps.timetable.instructor_conflicts import detect_instructor_conflicts
from apps.timetable.models import GeneratedSchedule
from apps.timetable.schedule_instructor import get_assignments, instructor_timetable
from apps.timetable.schedule_mapping import combine_and_sort_days, get_schedule_details
from apps.user.models import User
from apps.user.utils import get_template_by_user_type
from apps.user.common.group_members_utils import get_faculty_and_staff_info

@login_required
def dashboard(request):
    template = get_template_by_user_type(request.user, 'dashboard')
    
    # Greeting Message
    greeting_service = GreetingMessage()
    greeting_message = greeting_service.get_greeting_message()

    if template and request.user.user_type in [4]:
        institute = get_object_or_404(Institutes, user=request.user)
        program = get_object_or_404(Programs, user=request.user)
        curriculum_with_courses = CurriculumYear.objects.filter(
          courses__program=program
        ).order_by('-curriculum_id').first()
        
        if curriculum_with_courses:
          request.session['curriculum_id'] = curriculum_with_courses.curriculum_id
          program.curriculum_id = curriculum_with_courses.curriculum_id
        else:
          # No curriculum found, set a flag or handle accordingly
          program.curriculum_id = None  # Or set to a default value if needed
      
        user_info = get_faculty_and_staff_info(request)

        items_per_page = request.GET.get('items_per_page', 25)
        page_number = request.GET.get('page', 1)
        group_id = request.GET.get('group', None)

        # Validate items per page
        validated_items_per_page = validate_items_per_page(items_per_page, request, page_number, group_id)
        if isinstance(validated_items_per_page, HttpResponseRedirect):
            return validated_items_per_page
        # Update items per page
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # If AJAX request, return only the partial template
            return HttpResponse(render(request, 'partials/_faculty_staff_list.html', {
                'faculty_and_staff': user_info['faculty_and_staff'],
            }).content)
        
        # If standard request, return the full dashboard template
        return render(request, template, {
            **user_info,
            'greeting_message': greeting_message,
            'institute': institute,
        })
    
    elif template and request.user.user_type in [1, 2, 3]:
        return render(request, template)
    
    else:
        raise Http404("Template not found")

@login_required
def faculty_workload(request, username):
    template = get_template_by_user_type(request.user, 'faculty-workload')
    user = get_object_or_404(User, username=username)
    faculty_and_staff = User.objects.filter(institute=request.user.institute, program=request.user.program)
    program_name = request.user.program.program_name
    program_code = request.user.program.program_code
    institute_name = request.user.institute.institute_name
    selected_instructor_id = user.id
    view_mode = request.GET.get('view', 'table')

    generated_schedules = GeneratedSchedule.objects.filter(institute=request.user.institute).values('result_identification', 'academic_year', 'semester').order_by('-created_at')
    result_identification = request.GET.get('result_identification')
    if not result_identification or not GeneratedSchedule.objects.filter(result_identification=result_identification).exists():
            if generated_schedules.exists():
                result_identification = generated_schedules.first()['result_identification']
    instructor_timetable_data = instructor_timetable(selected_instructor_id, result_identification) if selected_instructor_id else {'instructor_timetable': []}
    if not instructor_timetable_data['instructor_timetable']:
        no_schedule = False
    else:
        no_schedule = True

    conflicts_data = detect_instructor_conflicts(instructor_timetable_data['instructor_timetable'])
    if template and request.user.user_type in [3, 4]:
        if "generate_pdf" in request.GET:
            return redirect(reverse('generate_pdf', args=[result_identification, selected_instructor_id]))
        
        return render(request, template, {
            'faculty_and_staff': faculty_and_staff,
            'program_name': program_name,
            'program_code': program_code,
            'institute_name': institute_name,
            'user': user,
            'generated_schedules': generated_schedules,
            'result_identification': result_identification,
            'selected_instructor_id': selected_instructor_id,
            **instructor_timetable_data,
            **conflicts_data,
            'view_mode': view_mode,
            'days': get_weekdays.get_ordered_weekdays(),
            'periods': get_periods.get_ordered_periods(),
            'no_schedule': no_schedule,
        })
    raise Http404
