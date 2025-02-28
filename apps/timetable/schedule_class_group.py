from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from apps.curriculum.models import Programs
from apps.timetable import get_weekdays
from apps.timetable.create_timetable import create_timetable_form
from apps.timetable.schedule_classroom import get_instructors_and_class_groups
from apps.timetable.update_timetable import update_timetable_form
from apps.timetable import get_periods
from apps.timetable.class_group_conflicts import detect_class_group_conflicts
from apps.timetable.forms import ResultClassGroupForm
from apps.timetable.get_selected_class_group import get_selected_class_group
from apps.timetable.get_selected_classroom import get_selected_classroom
from apps.timetable.get_selected_instructor import get_selected_instructor
from apps.timetable.models import ResultClassGroup, ResultClassroom, ResultCourse, ResultIdentification, ResultInstructor, ResultMeetingTime, ResultTimetable, ResultTimetableDetail
from apps.timetable.schedule_mapping import get_year_levels
from apps.user.utils import get_template_by_user_type
from apps.timetable.schedule_instructor import get_view_mode
from django.db import models

def class_group_timetable(selected_class_group_id, result_identification):
    result_identification = get_object_or_404(ResultIdentification, result_id=result_identification)
    class_group_timetable = ResultTimetable.objects.filter(result_identification=result_identification, class_group_id=selected_class_group_id).values('course_id', 'instructor_id', 'result_id', 'class_group_id')

    # Fetch all related objects in a single query
    course_ids = class_group_timetable.values_list('course_id', flat=True)
    instructor_ids = class_group_timetable.values_list('instructor_id', flat=True)
    timetable_ids = class_group_timetable.values_list('result_id', flat=True)
    class_group_ids = class_group_timetable.values_list('class_group_id', flat=True)

    courses = {course['course_id']: course for course in ResultCourse.objects.filter(result_identification=result_identification, course_id__in=course_ids).values('course_id', 'course_code', 'course_description')}
    instructors = {instructor['instructor_id']: instructor for instructor in ResultInstructor.objects.filter(result_identification=result_identification, instructor_id__in=instructor_ids).values('instructor_id', 'instructor_name')}
    class_groups = {class_group['class_group_id']: class_group for class_group in ResultClassGroup.objects.filter(result_identification=result_identification, class_group_id__in=class_group_ids).values('class_group_id', 'class_group_name')}
    timetable_details = ResultTimetableDetail.objects.filter(result_identification=result_identification, result_timetable_id__in=timetable_ids).values('room_id', 'meeting_id', 'result_timetable_id', 'result_id')
    room_ids = timetable_details.values_list('room_id', flat=True)
    meeting_ids = timetable_details.values_list('meeting_id', flat=True)

    classrooms = {classroom['room_id']: classroom for classroom in ResultClassroom.objects.filter(result_identification=result_identification, room_id__in=room_ids).values('room_id', 'room_name')}
    meeting_times = ResultMeetingTime.objects.filter(result_identification=result_identification, meeting_id__in=meeting_ids)

    timetable_data = {}

    for timetable_detail in timetable_details:
        timetable = next((t for t in class_group_timetable if t['result_id'] == timetable_detail['result_timetable_id']), {})
        course = courses.get(timetable.get('course_id'), {})
        classroom = classrooms.get(timetable_detail['room_id'], {})
        instructor = instructors.get(timetable.get('instructor_id'), {})
        class_group = class_groups.get(timetable.get('class_group_id'), {})

        if timetable_detail['meeting_id'] not in timetable_data:
            timetable_data[timetable_detail['meeting_id']] = {
                # Course
                'course_id': timetable.get('course_id', ''),
                'course_code': course.get('course_code', ''),
                'course_description': course.get('course_description', ''),
                # Classroom
                'room_name': classroom.get('room_name', ''),
                'room_id': timetable_detail.get('room_id', ''),
                # Meeting
                'meeting_day': set(),
                'meeting_time': '',
                'flexible_day': set(),
                'f2f_day': set(),
                'timetable_result_id': timetable.get('result_id', ''),
                'schedule': [],
                'meeting_id': timetable_detail.get('meeting_id', ''),
                'result_timetable_detail_id': timetable_detail.get('result_id', ''),
                'start_time': '',
                'end_time': '',
                'is_online_class': False,
                # Instructor
                'instructor_name': instructor.get('instructor_name', ''),
                'instructor_id': timetable.get('instructor_id', ''),
                # Class Group
                'class_group_id': timetable.get('class_group_id', ''),
                'class_group_name': class_group.get('class_group_name', ''),
                # Result Identification
                'result_identification': result_identification.result_id,
                
            }

        for meeting_time in meeting_times:
            if meeting_time.meeting_id == timetable_detail['meeting_id']:
                meeting_day = meeting_time.meeting_day
                start_time = meeting_time.start_time
                end_time = meeting_time.end_time
                formatted_time = f"{start_time} - {end_time}" if start_time and end_time else ''
                is_online_meeting = meeting_time.is_online_meeting
                print(f"IS_ONLINE_MEETING: {is_online_meeting}")
                timetable_data[timetable_detail['meeting_id']]['meeting_day'].add(meeting_day)
                timetable_data[timetable_detail['meeting_id']]['meeting_time'] = formatted_time
                timetable_data[timetable_detail['meeting_id']]['schedule'].append(f"{meeting_day}, {formatted_time}")
                timetable_data[timetable_detail['meeting_id']]['start_time'] = start_time
                timetable_data[timetable_detail['meeting_id']]['end_time'] = end_time
                timetable_data[timetable_detail['meeting_id']]['is_online_class'] = is_online_meeting
                timetable_data[timetable_detail['meeting_id']]['is_online_meeting'] = is_online_meeting
                if is_online_meeting:
                    timetable_data[timetable_detail['meeting_id']]['flexible_day'].add(meeting_day)
                else:
                    timetable_data[timetable_detail['meeting_id']]['f2f_day'].add(meeting_day)

    # Combine meeting days into a single entry
    combined_timetable_data = []
    for data in timetable_data.values():
        data['meeting_day'] = ', '.join(sorted(day for day in data['meeting_day'] if day is not None))
        data['flexible_day'] = ', '.join(sorted(day for day in data['flexible_day'] if day is not None))
        data['f2f_day'] = ', '.join(sorted(day for day in data['f2f_day'] if day is not None))
        combined_timetable_data.append(data)
    
    return {
        'class_group_timetable': combined_timetable_data
    }

@login_required
def schedule_class_groups(request, result_identification):
    view_mode = get_view_mode(request)
    # Call update_timetable_form and handle its response
    response = update_timetable_form(request)
    if isinstance(response, HttpResponseRedirect):
        return response
    
    # Call create_timetable_form and handle its response
    response = create_timetable_form(request, result_identification)
    if isinstance(response, HttpResponseRedirect):
        return response
    
    programs = Programs.objects.filter(institute=request.user.institute).values('program_name', 'program_code')
    template = get_template_by_user_type(request.user, 'schedule-class-groups')
    selected_year_level, selected_class_group_id = get_selected_class_group(request, result_identification)
    selected_classroom_type, selected_classroom_id = get_selected_classroom(request, result_identification)
    selected_instructor_id = get_selected_instructor(request, result_identification)
    year_levels = get_year_levels()
    class_group_timetable_data = class_group_timetable(selected_class_group_id, result_identification) if selected_class_group_id else {'class_group_timetable': []}
    class_groups_query = ResultClassGroup.objects.filter(result_identification=result_identification).values('class_group_name', 'class_group_id', 'year_level')
    if selected_year_level != 'all':
        class_groups_query = class_groups_query.filter(year_level=selected_year_level)
    class_groups_query = class_groups_query.order_by('class_group_name')
    class_groups = list(class_groups_query)

    if selected_class_group_id not in [str(cg['class_group_id']) for cg in class_groups]:
        selected_class_group_id = None

    if selected_class_group_id is None and class_groups:
        selected_class_group = class_groups[0]
        selected_class_group_id = str(selected_class_group['class_group_id'])
        request.session['selected_class_group_id'] = selected_class_group_id
    else:
        try:
            selected_class_group = next(cg for cg in class_groups if str(cg['class_group_id']) == selected_class_group_id)
            request.session['selected_class_group_id'] = selected_class_group_id
        except StopIteration:
            selected_class_group = None

    if request.method == 'POST':
        if 'AddClassGroupSubmit' in request.POST:
            class_group_form = ResultClassGroupForm(request.POST)
            if class_group_form.is_valid():
                new_class_group = class_group_form.save(commit=False)
                new_class_group.result_identification_id = result_identification
    
                # Get the selected program and year level from the form
                selected_program = request.POST.get('program_name')
                selected_year_level = request.POST.get('year_level')
    
                # Get the last class group for the selected program and year level
                last_group = ResultClassGroup.objects.filter(
                    result_identification=result_identification,
                    class_group_name__startswith=f"{selected_program} {selected_year_level}"
                ).order_by('-class_group_name').first()
    
                # Determine the next letter for the class group name
                if last_group:
                    last_letter = last_group.class_group_name[-1]
                    next_letter = chr(ord(last_letter) + 1)
                else:
                    next_letter = 'A'
    
                # Generate the new class group name
                new_class_group.class_group_name = f"{selected_program} {selected_year_level}{next_letter}"
                new_class_group.class_group_id = (ResultClassGroup.objects.aggregate(max_id=models.Max('class_group_id'))['max_id'] or 0) + 1
                new_class_group.save()
    
                messages.success(request, f'{new_class_group.class_group_name} has been added successfully.')
                return redirect(f'/timetable/scheduler/classgroups/{result_identification}/?class_group_id={new_class_group.class_group_id}&year_level=all')
            else:
                messages.error(request, 'An error occurred while adding the class group.')
             
        elif 'UpdateClassGroupSubmit' in request.POST:
            class_group_form = ResultClassGroupForm(request.POST)
            if class_group_form.is_valid():
                try:
                    class_group_to_edit = ResultClassGroup.objects.get(result_identification=result_identification, class_group_id=selected_class_group_id)
                    
                    # Get the selected program and year level from the form
                    selected_program = request.POST.get('program_name')
                    selected_year_level = request.POST.get('year_level')
                    
                    # Get the last class group for the selected program and year level
                    last_group = ResultClassGroup.objects.filter(
                        result_identification=result_identification,
                        class_group_name__startswith=f"{selected_program} {selected_year_level}"
                    ).order_by('-class_group_name').first()
                    
                    # Determine the next letter for the class group name
                    if last_group:
                        last_letter = last_group.class_group_name[-1]
                        next_letter = chr(ord(last_letter) + 1)
                    else:
                        next_letter = 'A'
                    
                    # Store the old class group name
                    old_class_group_name = class_group_to_edit.class_group_name

                    # Generate the new class group name
                    class_group_to_edit.class_group_name = f"{selected_program} {selected_year_level}{next_letter}"
                    class_group_to_edit.year_level = class_group_form.cleaned_data['year_level']
                    class_group_to_edit.save()
                    
                    messages.info(request, f"Class group name changed from {old_class_group_name} to {class_group_to_edit.class_group_name}.")
                    messages.success(request, f'{class_group_to_edit.class_group_name} has been updated successfully.')
                    return redirect(f'/timetable/scheduler/classgroups/{result_identification}/?class_group_id={class_group_to_edit.class_group_id}&year_level=all')
                except ResultClassGroup.DoesNotExist:
                    messages.error(request, 'Class group does not exist.')
                    
        elif 'DeleteClassGroupSubmit' in request.POST:
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                try:
                    class_group_to_delete = ResultClassGroup.objects.get(result_identification=result_identification, class_group_id=selected_class_group_id)
                    selected_program = class_group_to_delete.class_group_name.split()[0]
                    selected_year_level = class_group_to_delete.class_group_name.split()[1][0]
                    
                    # Delete the selected class group
                    class_group_to_delete.delete()
                    
                    # Retrieve the remaining class groups for the same program and year level
                    remaining_class_groups = ResultClassGroup.objects.filter(
                        result_identification=result_identification,
                        class_group_name__startswith=f"{selected_program} {selected_year_level}"
                    ).order_by('class_group_name')
                    
                    # Rename the remaining class groups in alphabetical order
                    next_letter = 'A'
                    for class_group in remaining_class_groups:
                        class_group.class_group_name = f"{selected_program} {selected_year_level}{next_letter}"
                        class_group.save()
                        next_letter = chr(ord(next_letter) + 1)
                    messages.info(request, f'Deleted class sets automatically reordered the remaining classes alphabetically within that year level.')
                    messages.success(request, f'{class_group_to_delete.class_group_name} has been deleted successfully.')
                    return redirect(request.get_full_path())
                except ResultClassGroup.DoesNotExist:
                    messages.error(request, 'Class group does not exist.')
            else:
                messages.error(request, 'Invalid password. Please try again.')
    else:
        class_group_form = ResultClassGroupForm()
        
    conflicts_data = detect_class_group_conflicts(class_group_timetable_data['class_group_timetable'])
    add_schedule = get_instructors_and_class_groups(request, result_identification)
    if template and request.user.user_type == 4:
        return render(request, template, {
            'days': get_weekdays.get_ordered_weekdays(),
            'periods': get_periods.get_ordered_periods(),
            'result_identification': result_identification,
            'class_groups': class_groups,
            'selected_class_group': selected_class_group,
            'selected_class_group_id': selected_class_group_id,
            'selected_classroom_type': selected_classroom_type,
            'selected_classroom_id': selected_classroom_id,
            'selected_year_level': selected_year_level,
            'year_levels': year_levels,
            'selected_instructor_id': selected_instructor_id,
            **class_group_timetable_data,
            **conflicts_data,
            **add_schedule,
            'programs': programs,
            'view_mode': view_mode,
        })
    raise Http404