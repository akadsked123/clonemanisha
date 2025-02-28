from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from apps.timetable import get_periods, get_weekdays
from apps.timetable.create_timetable import create_timetable_form
from apps.timetable.update_timetable import update_timetable_form
from apps.timetable.classroom_conflicts import detect_classroom_conflicts
from apps.timetable.get_selected_class_group import get_selected_class_group
from apps.timetable.get_vacant_time_classroom import get_vacant_time_slots
from .forms import ResultClassroomForm
from .models import ResultClassGroup, ResultClassroom, ResultCourse, ResultIdentification, ResultInstructor, ResultMeetingTime, ResultTimetable, ResultTimetableDetail
from apps.timetable.get_selected_classroom import get_selected_classroom
from apps.timetable.get_selected_instructor import get_selected_instructor
from apps.user.utils import get_template_by_user_type
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.db.models import OuterRef, Subquery
from django.contrib.auth import get_user_model
from apps.timetable.schedule_instructor import get_view_mode 

def classroom_timetable(selected_classroom_id, result_identification):
    result_identification = get_object_or_404(ResultIdentification, result_id=result_identification)
    classroom_timetable = ResultTimetableDetail.objects.filter(result_identification=result_identification, room_id=selected_classroom_id).values('result_timetable_id', 'room_id', 'meeting_id', 'result_id')

    # Fetch all related objects in a single query
    timetable_ids = classroom_timetable.values_list('result_timetable_id', flat=True)
    meeting_ids = classroom_timetable.values_list('meeting_id', flat=True)

    timetables = {timetable['result_id']: timetable for timetable in ResultTimetable.objects.filter(result_identification=result_identification, result_id__in=timetable_ids).values('result_id', 'course_id', 'class_group_id', 'instructor_id')}
    courses = {course['course_id']: course for course in ResultCourse.objects.filter(result_identification=result_identification, course_id__in=[timetable['course_id'] for timetable in timetables.values()]).values('course_id', 'course_code', 'course_description')}
    class_groups = {class_group['class_group_id']: class_group for class_group in ResultClassGroup.objects.filter(result_identification=result_identification, class_group_id__in=[timetable['class_group_id'] for timetable in timetables.values()]).values('class_group_id', 'class_group_name')}
    instructors = {instructor['instructor_id']: instructor for instructor in ResultInstructor.objects.filter(result_identification=result_identification, instructor_id__in=[timetable['instructor_id'] for timetable in timetables.values()]).values('instructor_id', 'instructor_name')}
    meeting_times = ResultMeetingTime.objects.filter(result_identification=result_identification, meeting_id__in=meeting_ids)
    classrooms = {classroom['room_id']: classroom for classroom in ResultClassroom.objects.filter(result_identification=result_identification, room_id__in=[selected_classroom_id]).values('room_id', 'room_name')}

    timetable_data = {}

    for timetable_detail in classroom_timetable:
        timetable = timetables.get(timetable_detail['result_timetable_id'], {})
        course = courses.get(timetable.get('course_id'), {})
        class_group = class_groups.get(timetable.get('class_group_id'), {})
        instructor = instructors.get(timetable.get('instructor_id'), {})
        classroom = classrooms.get(timetable_detail['room_id'], {})

        if timetable_detail['meeting_id'] not in timetable_data:
            timetable_data[timetable_detail['meeting_id']] = {
                'course_code': course.get('course_code', ''),
                'course_description': course.get('course_description', ''),
                'class_group_name': class_group.get('class_group_name', ''),
                'meeting_day': set(),
                'meeting_time': '',
                'flexible_day': set(),
                'f2f_day': set(),
                'instructor_name': instructor.get('instructor_name', ''),
                'room_name': classroom.get('room_name', ''),
                'timetable_result_id': timetable.get('result_id', ''),
                'timetable_result_detail_id': timetable_detail['result_id'],
                'instructor_id': timetable.get('instructor_id', ''),
                'room_id': timetable_detail['room_id'],
                'start_time': '',
                'end_time': '',
                'result_identification': result_identification.result_id,
            }

        for meeting_time in meeting_times:
            if meeting_time.meeting_id == timetable_detail['meeting_id']:
                meeting_day = meeting_time.meeting_day
                start_time = meeting_time.start_time
                end_time = meeting_time.end_time
                formatted_time = f"{start_time} - {end_time}" if start_time and end_time else ''
                is_online_meeting = meeting_time.is_online_meeting

                timetable_data[timetable_detail['meeting_id']]['meeting_day'].add(meeting_day)
                timetable_data[timetable_detail['meeting_id']]['meeting_time'] = formatted_time
                timetable_data[timetable_detail['meeting_id']]['start_time'] = start_time
                timetable_data[timetable_detail['meeting_id']]['end_time'] = end_time
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
        'classroom_timetable': combined_timetable_data
    }
    
User = get_user_model()
def get_instructors_and_class_groups(request, result_identification):
    instructors = ResultInstructor.objects.filter(result_identification=result_identification).values('instructor_id', 'instructor_name').annotate(
        program_code=Subquery(
            User.objects.filter(id=OuterRef('instructor_id')).values('program__program_code')[:1]
        )
    ).order_by('instructor_name')
    classrooms = ResultClassroom.objects.filter(result_identification=result_identification).values('room_id', 'room_name', 'is_lab').order_by('room_name')
    class_groups = ResultClassGroup.objects.filter(
        result_identification=result_identification,
        schedule_courses__program=request.user.program
    ).distinct().values('class_group_id', 'class_group_name', 'year_level').order_by('class_group_name')
    
    # Get the selected class group ID from the request
    selected_class_group_id = request.session['selected_class_group_id']
    
    # Get the year level of the selected class group
    selected_class_group = ResultClassGroup.objects.filter(result_identification=result_identification, class_group_id=selected_class_group_id).first()
    selected_year_level = selected_class_group.year_level if selected_class_group else None
    
    # Filter courses based on the selected year level and class group name
    if selected_year_level and selected_class_group:
        print(selected_class_group_id)
        print(selected_class_group.class_group_name)
        class_group_name = selected_class_group.class_group_name
        print(class_group_name)
        program_code = class_group_name[:4]
          # Get the first four letters of the class group name (e.g., BSIT, BSIS)
        
        if program_code in ['BSIT', 'BSIS']:
            print(program_code)
            courses = ResultCourse.objects.filter(
                result_identification=result_identification,
                program__program_code=program_code,
                year_level=selected_year_level
            ).values('course_id', 'course_code', 'course_description').order_by('course_code')
        else:
            courses = []
    else:
        courses = []

    print(courses)
    print(f"CLASSROOMS: {classrooms}")
    print(f"INSTRUCTORS: {instructors}")

    return {
        'instructors_options': list(instructors),
        'class_groups_options': list(class_groups),
        'classrooms_options': list(classrooms),
        'courses_options': list(courses)
    }

   

@login_required
def schedule_classrooms(request, result_identification):
    view_mode = get_view_mode(request)
    # Call update_timetable_form and handle its response
    response = update_timetable_form(request)
    if isinstance(response, HttpResponseRedirect):
        return response
    
    # Call create_timetable_form and handle its response
    response = create_timetable_form(request, result_identification)
    if isinstance(response, HttpResponseRedirect):
        return response
    
    template = get_template_by_user_type(request.user, 'schedule-classrooms')
    selected_classroom_type, selected_classroom_id = get_selected_classroom(request, result_identification)
    selected_year_level, selected_class_group_id = get_selected_class_group(request, result_identification)
    selected_instructor_id = get_selected_instructor(request, result_identification)
    classrooms_query = ResultClassroom.objects.filter(result_identification=result_identification).values('room_name', 'room_id', 'is_lab')
    classroom_timetable_data = classroom_timetable(selected_classroom_id, result_identification) if selected_classroom_id else {'classroom_timetable': []}
    vacant_times = get_vacant_time_slots(classroom_timetable_data['classroom_timetable'], [day.day_name for day in get_weekdays.get_ordered_weekdays()]) if 'classroom_timetable' in classroom_timetable_data else {}
    conflicts_data = detect_classroom_conflicts(classroom_timetable_data['classroom_timetable'])
    if selected_classroom_type == 'laboratory':
        classrooms_query = classrooms_query.filter(is_lab=True)
    elif selected_classroom_type == 'lecture':
        classrooms_query = classrooms_query.filter(is_lab=False)
    
    classrooms = classrooms_query

    selected_classroom = None
    if selected_classroom_id:
        try:
            selected_classroom = ResultClassroom.objects.values('room_name', 'room_id', 'is_lab').get(
                result_identification=result_identification,
                room_id=selected_classroom_id)
            if (selected_classroom_type == 'laboratory' and not selected_classroom['is_lab']) or \
               (selected_classroom_type == 'lecture' and selected_classroom['is_lab']):
                selected_classroom = None
        except ResultClassroom.DoesNotExist:
            selected_classroom = None

    if not selected_classroom:
        selected_classroom = classrooms.first()
        if selected_classroom:
            selected_classroom_id = selected_classroom['room_id']
            request.session['selected_classroom_id'] = selected_classroom_id

    if request.method == 'POST':
        classroom_form = ResultClassroomForm(request.POST)
        if 'AddClassroomSubmit' in request.POST:
            if classroom_form.is_valid():
                new_classroom = classroom_form.save(commit=False)
                new_classroom.result_identification_id = result_identification
                new_classroom.is_lab = 'is_lab' in request.POST
                last_room = ResultClassroom.objects.filter(result_identification=result_identification).order_by('-room_id').first()
                new_classroom.room_id = (last_room.room_id + 1) if last_room else 1
                new_classroom.save()
                messages.success(request, f'{new_classroom.room_name} has been added successfully.')
                return redirect(f'/timetable/scheduler/classrooms/{result_identification}/?classroom_id={new_classroom.room_id}&classroom_type=all')
            else:
                messages.error(request, 'An error occurred while adding the classroom.')
        elif 'UpdateClassroomSubmit' in request.POST:
            if classroom_form.is_valid():
                try:
                    classroom_to_edit = ResultClassroom.objects.get(result_identification=result_identification, room_id=selected_classroom_id)
                    classroom_to_edit.room_name = classroom_form.cleaned_data['room_name']
                    classroom_to_edit.is_lab = 'is_lab' in request.POST
                    classroom_to_edit.save()
                    messages.success(request, f'{classroom_to_edit.room_name} has been updated successfully.')
                    return redirect(request.get_full_path())
                except ResultClassroom.DoesNotExist:
                    messages.error(request, 'Classroom does not exist.')
        elif 'DeleteClassroomSubmit' in request.POST:
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                try:
                    classroom_to_delete = ResultClassroom.objects.get(result_identification=result_identification, room_id=selected_classroom_id)
                    classroom_to_delete.delete()
                    messages.success(request, f'{classroom_to_delete.room_name} has been deleted successfully.')
                    return redirect(request.get_full_path())
                except ResultClassroom.DoesNotExist:
                    messages.error(request, 'Classroom does not exist.')
            else:
                messages.error(request, 'Invalid password. Please try again.')
    else:
        classroom_form = ResultClassroomForm()
    
# initial: providing option for adding schedule 
    add_schedule = get_instructors_and_class_groups(request, result_identification)
    if template and request.user.user_type == 4:
        return render(request, template, {
            'days':  get_weekdays.get_ordered_weekdays(),
            'periods': get_periods.get_ordered_periods(),
            'result_identification': result_identification,
            'classrooms': classrooms,
            'selected_classroom': selected_classroom,
            'selected_classroom_id': selected_classroom_id,
            'selected_classroom_type': selected_classroom_type,
            'selected_class_group_id': selected_class_group_id,
            'selected_year_level': selected_year_level,
            'selected_instructor_id': selected_instructor_id,
            **classroom_timetable_data,
            'vacant_times': vacant_times,
            **conflicts_data,
            **add_schedule,
            'view_mode': view_mode,
        })
    raise Http404