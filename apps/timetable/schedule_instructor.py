import os
import random
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from apps.timetable import get_periods, get_weekdays
from apps.timetable.get_selected_class_group import get_selected_class_group
from apps.timetable.get_selected_instructor import get_selected_instructor
from apps.timetable.instructor_conflicts import detect_instructor_conflicts
from apps.timetable.models import InitialCourseAssignment, ResultClassGroup, ResultClassroom, ResultCourse, ResultIdentification, ResultInstructor, ResultMeetingTime, ResultTimetable, ResultTimetableDetail, ViewTimetable
from apps.timetable.schedule_classroom import get_selected_classroom
from apps.timetable.update_timetable import update_timetable_form
from apps.timetable.users_list_utils import get_new_user_list
from apps.user.common.user_notification import create_notification
from apps.user.models import User
from apps.user.utils import get_template_by_user_type
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse, HttpResponseRedirect

def get_view_mode(request):
    view_mode = request.GET.get('view')
    if view_mode:
        request.session['view_mode'] = view_mode
    else:
        view_mode = request.session.get('view_mode', 'table')
    return view_mode

def instructor_timetable_for_all_conflicts(result_identification):
    result_identification_obj = get_object_or_404(ResultIdentification, result_id=result_identification)
    
    instructor_timetable = ResultTimetable.objects.filter(result_identification=result_identification_obj).values('course_id', 'result_id', 'class_group_id', 'instructor_id')

    # Fetch all related objects in a single query
    course_ids = instructor_timetable.values_list('course_id', flat=True)
    timetable_ids = instructor_timetable.values_list('result_id', flat=True)
    class_group_ids = instructor_timetable.values_list('class_group_id', flat=True)

    courses = {course['course_id']: course for course in ResultCourse.objects.filter(result_identification=result_identification_obj, course_id__in=course_ids).values('course_id', 'course_code', 'course_description', 'credit_units', 'year_level', 'result_id')}
    class_groups = {class_group['class_group_id']: class_group for class_group in ResultClassGroup.objects.filter(result_identification=result_identification_obj, class_group_id__in=class_group_ids).values('class_group_id', 'class_group_name')}
    timetable_details = ResultTimetableDetail.objects.filter(result_identification=result_identification_obj, result_timetable_id__in=timetable_ids).values('room_id', 'meeting_id', 'result_timetable_id', 'result_id')
    room_ids = timetable_details.values_list('room_id', flat=True)
    meeting_ids = timetable_details.values_list('meeting_id', flat=True)

    classrooms = {classroom['room_id']: classroom for classroom in ResultClassroom.objects.filter(result_identification=result_identification_obj, room_id__in=room_ids).values('room_id', 'room_name')}
    meeting_times = {meeting_time['meeting_id']: meeting_time for meeting_time in ResultMeetingTime.objects.filter(result_identification=result_identification_obj, meeting_id__in=meeting_ids).values('meeting_id', 'meeting_day', 'start_time', 'end_time', 'is_online_meeting')}

    total_units = 0
    timetable_data = {}
    processed_timetable_ids = set()

    for timetable_detail in timetable_details:
        timetable = next((t for t in instructor_timetable if t['result_id'] == timetable_detail['result_timetable_id']), {})
        course = courses.get(timetable.get('course_id'), {})
        classroom = classrooms.get(timetable_detail['room_id'], {})
        class_group = class_groups.get(timetable.get('class_group_id'), {})
        meeting_time = meeting_times.get(timetable_detail['meeting_id'], {})

        key = (timetable.get('course_id'), timetable.get('class_group_id'))
        if key not in timetable_data:
            timetable_data[key] = {
                'course_id': course.get('course_id', ''),
                'year_level': course.get('year_level', ''),
                'course_code': course.get('course_code', ''),
                'course_description': course.get('course_description', ''),
                'units': course.get('credit_units', 0),
                'class_group_name': class_group.get('class_group_name', ''),
                'room_name': classroom.get('room_name', ''),
                'schedule': [],
                'class_group_id': timetable.get('class_group_id', ''),
                'course_id': timetable.get('course_id', ''),
                'result_id': timetable.get('result_id', ''),
                'result_course_id': course.get('result_id', ''),
                'result_identification': result_identification,
                'timetable_result_id': timetable.get('result_id', ''),
                'timetable_result_detail_id': timetable_detail.get('result_id', ''),
                'instructor_id': timetable.get('instructor_id', ''),
                'room_id': timetable_detail.get('room_id', ''),
                'start_time': meeting_time.get('start_time', ''),
                'end_time': meeting_time.get('end_time', ''),
                'meeting_day': meeting_time.get('meeting_day', ''),
            }

        for meeting_time in meeting_times.values():
            if meeting_time['meeting_id'] == timetable_detail['meeting_id']:
                meeting_day = meeting_time['meeting_day']
                start_time = meeting_time['start_time']
                end_time = meeting_time['end_time']
                formatted_time = f"{start_time} - {end_time}" if start_time and end_time else ''
                room_name = "ONLINE" if meeting_time['is_online_meeting'] else classroom.get('room_name', '')
                timetable_data[key]['schedule'].append(f"{room_name}, {meeting_day}, {formatted_time}")

        if timetable_detail['result_timetable_id'] not in processed_timetable_ids:
            total_units += course.get('credit_units', 0)
            processed_timetable_ids.add(timetable_detail['result_timetable_id'])

    return {
        'instructor_timetable': list(timetable_data.values()),
        'total_units': total_units
    }
    

def instructor_timetable(selected_instructor_id, result_identification):
    result_identification_obj = get_object_or_404(ResultIdentification, result_id=result_identification)
    instructor_timetable = ResultTimetable.objects.filter(result_identification=result_identification_obj, instructor=selected_instructor_id).values('course_id', 'result_id', 'class_group_id')

    # Fetch all related objects in a single query
    course_ids = instructor_timetable.values_list('course_id', flat=True)
    timetable_ids = instructor_timetable.values_list('result_id', flat=True)
    class_group_ids = instructor_timetable.values_list('class_group_id', flat=True)

    courses = {course['course_id']: course for course in ResultCourse.objects.filter(result_identification=result_identification_obj, course_id__in=course_ids).values('course_id', 'course_code', 'course_description', 'credit_units', 'year_level', 'result_id', 'laboratory_hours', 'lecture_hours')}
    class_groups = {class_group['class_group_id']: class_group for class_group in ResultClassGroup.objects.filter(result_identification=result_identification_obj, class_group_id__in=class_group_ids).values('class_group_id', 'class_group_name')}
    timetable_details = ResultTimetableDetail.objects.filter(result_identification=result_identification_obj, result_timetable_id__in=timetable_ids).values('room_id', 'meeting_id', 'result_timetable_id', 'result_id')
    room_ids = timetable_details.values_list('room_id', flat=True)
    meeting_ids = timetable_details.values_list('meeting_id', flat=True)

    classrooms = {classroom['room_id']: classroom for classroom in ResultClassroom.objects.filter(result_identification=result_identification_obj, room_id__in=room_ids).values('room_id', 'room_name')}
    meeting_times = {meeting_time['meeting_id']: meeting_time for meeting_time in ResultMeetingTime.objects.filter(result_identification=result_identification_obj, meeting_id__in=meeting_ids).values('meeting_id', 'meeting_day', 'start_time', 'end_time', 'is_online_meeting')}

    total_units = 0
    timetable_data = {}
    processed_timetable_ids = set()

    for timetable_detail in timetable_details:
        timetable = next((t for t in instructor_timetable if t['result_id'] == timetable_detail['result_timetable_id']), {})
        course = courses.get(timetable.get('course_id'), {})
        classroom = classrooms.get(timetable_detail['room_id'], {})
        class_group = class_groups.get(timetable.get('class_group_id'), {})
        meeting_time = meeting_times.get(timetable_detail['meeting_id'], {})

        key = (timetable.get('course_id'), timetable.get('class_group_id'))
        if key not in timetable_data:
            timetable_data[key] = {
                'course_id': course.get('course_id', ''),
                'year_level': course.get('year_level', ''),
                'course_code': course.get('course_code', ''),
                'course_description': course.get('course_description', ''),
                'units': course.get('credit_units', 0),
                'class_group_name': class_group.get('class_group_name', ''),
                'room_name': classroom.get('room_name', ''),
                'schedule': [],
                'class_group_id': timetable.get('class_group_id', ''),
                'course_id': timetable.get('course_id', ''),
                'result_id': timetable.get('result_id', ''),
                'result_course_id': course.get('result_id', ''),
                'result_identification': result_identification,
                'timetable_result_id': timetable.get('result_id', ''),
                'timetable_result_detail_id': timetable_detail.get('result_id', ''),
                'instructor_id': selected_instructor_id,
                'room_id': timetable_detail.get('room_id', ''),
                'start_time': meeting_time.get('start_time', ''),
                'end_time': meeting_time.get('end_time', ''),
                'meeting_day': meeting_time.get('meeting_day', ''),
                'meeting_time': f"{meeting_time.get('start_time', '')} - {meeting_time.get('end_time', '')}",
                'is_online_meeting': meeting_time.get('is_online_meeting', False),
                'timetable_view': []
            }

        for meeting_time in meeting_times.values():
            if meeting_time['meeting_id'] == timetable_detail['meeting_id']:
                meeting_day = meeting_time['meeting_day']
                start_time = meeting_time['start_time']
                end_time = meeting_time['end_time']
                formatted_time = f"{start_time} - {end_time}" if start_time and end_time else ''
                room_name = "ONLINE" if meeting_time['is_online_meeting'] else classroom.get('room_name', '')
                timetable_data[key]['schedule'].append(f"{room_name}, {meeting_day}, {formatted_time}"),
                timetable_data[key]['timetable_view'].append({
                    'room_name': room_name,
                    'class_group_id': timetable.get('class_group_id', ''),
                    'room_id': timetable_detail.get('room_id', ''),
                    'meeting_time': formatted_time,
                    'meeting_day': meeting_day,
                    'timetable_result_id': timetable.get('result_id', ''),
                    'timetable_result_detail_id': timetable_detail.get('result_id', ''),
                    'instructor_id': selected_instructor_id,
                    'start_time': meeting_time.get('start_time', ''),
                    'end_time': meeting_time.get('end_time', ''),
                    'result_identification': result_identification,
                    'course_id': timetable.get('course_id', ''),
                    'course_code': course.get('course_code', ''),
                    'credit_units': course.get('credit_units', 0),
                    'lab_units': course.get('laboratory_hours', 0),
                    'lec_units': course.get('lecture_hours', 0),
                    'course_description': course.get('course_description', ''),
                    'class_group_name': class_group.get('class_group_name', ''),
                    'is_online_meeting': meeting_time.get('is_online_meeting', False),
                })

        if timetable_detail['result_timetable_id'] not in processed_timetable_ids:
            total_units += course.get('credit_units', 0)
            processed_timetable_ids.add(timetable_detail['result_timetable_id'])

    return {
        'instructor_timetable': list(timetable_data.values()),
        'total_units': total_units
    }

def get_assignments(result_identification, instructor_id):
    assignments = InitialCourseAssignment.objects.filter(
        result_identification_id=result_identification,
        instructor_id=instructor_id,
        is_assign=True
    ).select_related('course_id').values(
        'assignment_id',
        'course_id__course_code', 
        'course_id__course_description', 
        'course_id__result_id', 
        'course_id__credit_units',
        'course_id__year_level',
        'course_id__course_id'
    )
    
    total_credit_units = sum(assignment['course_id__credit_units'] for assignment in assignments)
    
    warnings = []
    for assignment in assignments:
        warnings.append(f"{assignment['course_id__course_code']} has no assigned class group, room, and day and time.")
    
    total_warnings = len(warnings)
    
    return assignments, total_credit_units, warnings, total_warnings


def select_class_group(result_identification, year_level):
    result_identification_obj = get_object_or_404(ResultIdentification, result_id=result_identification)
    class_group_options = ResultClassGroup.objects.filter(result_identification=result_identification_obj, year_level=year_level).values('class_group_id', 'class_group_name')
    
    return list(class_group_options)

@login_required
def schedule_instructors(request, result_identification):
    view_mode = get_view_mode(request)
        # Call update_timetable_form and handle its response
    response = update_timetable_form(request)
    if isinstance(response, HttpResponseRedirect):
        return response
    selected_classroom_type, selected_classroom_id = get_selected_classroom(request, result_identification)
    selected_year_level, selected_class_group_id = get_selected_class_group(request, result_identification)
    selected_instructor_id = get_selected_instructor(request, result_identification)
    instructor_list = get_new_user_list(request, result_identification)
    is_shared = ViewTimetable.objects.filter(result_identification=ResultIdentification.objects.get(result_id=result_identification), share_to_instructor=True, user=User.objects.get(id=selected_instructor_id)).exists()
    template = get_template_by_user_type(request.user, 'schedule-instructors')
    instructor_query = ResultInstructor.objects.filter(result_identification=result_identification).values('instructor_id', 'instructor_name').order_by('instructor_name')
    assignments, total_unit_assignments, warnings, total_warnings = get_assignments(result_identification, selected_instructor_id)
    selected_instructor = None
    if selected_instructor_id:
        selected_instructor = User.objects.filter(id=selected_instructor_id).only('first_name', 'middle_name', 'last_name', 'email', 'profile_image').first()

    instructor_timetable_data = instructor_timetable(selected_instructor_id, result_identification) if selected_instructor_id else {'instructor_timetable': []}
    conflicts_data = detect_instructor_conflicts(instructor_timetable_data['instructor_timetable'], warnings, total_warnings)

    if request.method == 'POST':
        if 'AddNewInstructorSubmit' in request.POST:
            instructor_ids = request.POST.getlist('instructor')
            if not instructor_ids:
                messages.info(request, "No instructors selected.")
                return redirect(request.get_full_path())
            
            users = User.objects.filter(id__in=instructor_ids)
            existing_instructors = ResultInstructor.objects.filter(result_identification=result_identification, instructor__in=users).values_list('instructor_id', flat=True)
            new_instructors = [
                ResultInstructor(
                    result_identification_id=result_identification,
                    instructor=user,
                    instructor_name=f"{user.first_name} {user.middle_name or ''} {user.last_name}".strip()
                )
                for user in users if user.id not in existing_instructors
            ]
            if new_instructors:
                ResultInstructor.objects.bulk_create(new_instructors)
                messages.success(request, "Instructors added successfully.")
                selected_instructor = random.choice(new_instructors)
                return redirect(reverse('timetable:scheduler-instructors', kwargs={'result_identification': result_identification}) + f'?instructor_id={selected_instructor.instructor.id}')
            else:
                messages.info(request, "All selected instructors are already added.")
                return redirect(request.get_full_path())

        if 'UnassignInstructorSubmit' in request.POST:
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                instructor_id = request.POST.get('instructor_id')
                instructor = User.objects.get(id=request.POST.get('instructor_id'))
                if instructor_id:
                    result_identification_obj = get_object_or_404(ResultIdentification, result_id=result_identification)
                    
                    # Check if the instructor_id exists in ResultTimetable before updating to None
                    if ResultTimetable.objects.filter(result_identification=result_identification_obj,instructor_id=instructor_id).exists():
                        ResultTimetable.objects.filter(result_identification=result_identification_obj,instructor_id=instructor_id).update(instructor=None)
                    
                    # Check if the result_identification exists in InitialCourseAssignment
                    if InitialCourseAssignment.objects.filter(result_identification=result_identification_obj,instructor_id=instructor_id).exists():
                        InitialCourseAssignment.objects.filter(result_identification=result_identification_obj,instructor_id=instructor_id).delete()
                    
                    # Unshare the schedule with the instructor
                    view_timetable = ViewTimetable.objects.filter(result_identification=result_identification_obj,user_id=instructor_id).first()
                    if view_timetable:
                        view_timetable.share_to_instructor = False
                        view_timetable.save()
                    else:
                        view_timetable = ViewTimetable(result_identification=result_identification_obj,user_id=instructor_id,share_to_instructor=False)
                        view_timetable.save()
                    
                    create_notification(
                        recipient=instructor,
                        message="The program chairperson has decided to unassign you from the schedules, and you will no longer have access to view them.",
                        status=1,
                        sender=request.user,
                        notification_url=f'/user/notification/{instructor.username}'
                    )
                    ResultInstructor.objects.filter(result_identification=result_identification, instructor_id=instructor_id).delete()
                    instructor = User.objects.get(id=instructor_id)
                    messages.success(request, f"{instructor.get_full_name()} unassigned successfully.")
                    return redirect(request.get_full_path())
                else:
                    messages.info(request, "No instructor selected for unassignment.")
                    return redirect(request.get_full_path())
            else:
                messages.error(request, 'Invalid password. Please try again.')
                return redirect(request.get_full_path())
            
        if 'ShareSchedule' in request.POST:
            user = User.objects.get(id=request.POST.get('instructor_id'))
            result_identification_obj = ResultIdentification.objects.get(result_id=request.POST.get('result_identification'))
            view_timetable, created = ViewTimetable.objects.get_or_create(
                result_identification=result_identification_obj,
                user=user,
                defaults={'share_to_instructor': True}
            )
            if not created:
                view_timetable.share_to_instructor = True
                view_timetable.save()
                messages.success(request, f"Schedule updated and shared with {user.get_full_name()}")
            else:
                messages.success(request, f"Schedule shared with {user.get_full_name()}")
        
            create_notification(recipient=user, message="You have been shared a schedule by the program chairperson.", status=1, sender=request.user, notification_url=f'/user/notification/{user.username}')
            return redirect(request.get_full_path())
        
        if 'UnshareSchedule' in request.POST:
            user = User.objects.get(id=request.POST.get('instructor_id'))
            result_identification_obj = ResultIdentification.objects.get(result_id=request.POST.get('result_identification'))
            view_timetable = ViewTimetable.objects.filter(
                result_identification=result_identification_obj,
                user=user
            ).first()
            if view_timetable:
                view_timetable.share_to_instructor = False
                view_timetable.save()
                messages.success(request, f"Schedule unshared with {user.get_full_name()}")
            else:
                view_timetable = ViewTimetable(
                    result_identification=result_identification_obj,
                    user=user,
                    share_to_instructor=False
                )
                view_timetable.save()
                messages.success(request, f"Schedule unshared with {user.get_full_name()}")
        
            create_notification(recipient=user, message="The schedule shared with you has changes that need to be reviewed, so the program chairperson will unshare it with you.", status=1, sender=request.user, notification_url=f'/user/notification/{user.username}')
            return redirect(request.get_full_path())

        if 'UnassignCourseSubmit' in request.POST:
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                assignment_id = request.POST.get('assignment_id')
                if assignment_id:
                    # Delete the data from InitialCourseAssignment
                    InitialCourseAssignment.objects.filter(assignment_id=assignment_id).delete()
                    messages.success(request, f"Course unassigned successfully from the instructor.")
                else:
                    # set null to instructor_id in ResultTimetable
                    result_id = request.POST.get('result_id')
                    ResultTimetable.objects.filter(result_id=result_id,).update(instructor=None)
                    messages.success(request, f"Course unassigned successfully from the instructor.")
            else:
                messages.error(request, 'Invalid password. Please try again.')
            return redirect(request.get_full_path())
          
        if 'AssignCourseSubmit' in request.POST:
            result_identification_id = request.POST.get('result_identification_id')
            instructor_id = request.POST.get('instructor_id')
            selected_course_ids = request.POST.getlist('selected_course_id')
        
            result_identification = ResultIdentification.objects.get(result_id=result_identification_id)
            instructor = User.objects.get(id=instructor_id)
        
            for course_id in selected_course_ids:
                course = ResultCourse.objects.get(result_identification=result_identification, course_id=course_id)
                InitialCourseAssignment.objects.create(
                    result_identification=result_identification,
                    course_id=course,
                    instructor=instructor,
                    is_assign=True
                )
                messages.success(request, f'{course.course_description} assigned successfully to {instructor.get_full_name()}.')
            return redirect(request.get_full_path())
        
        if 'PermanentlyDeleteSchedule' in request.POST:
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                result_id = request.POST.get('result_id')
                result_identification_obj = get_object_or_404(ResultIdentification, result_id=result_identification)

                # Delete related ResultTimetableDetail entries
                ResultTimetable.objects.filter(result_identification=result_identification_obj, result_id=result_id).delete()
                  
                messages.success(request, 'Schedule has been permanently deleted.')
            else:
                messages.error(request, 'Invalid password. Please try again.')
            return redirect(request.get_full_path())
        
        if 'AddTimetableSubmit' in request.POST: 
            course_ids = request.POST.getlist('course_id[]')
            result_identification_ids = request.POST.getlist('result_identification[]')
            instructor_ids = request.POST.getlist('instructor_id[]')
            class_group_ids = request.POST.getlist('class_group_id[]')
            classroom_ids = request.POST.getlist('classroom_id[]')
            meeting_days = request.POST.getlist('meeting_day[]')
            start_times = request.POST.getlist('start_time[]')
            end_times = request.POST.getlist('end_time[]')
            is_online_classes = request.POST.getlist('is_online_class[]')
            timetable_result_ids = request.POST.getlist('timetable-result-id-for-update[]')
            result_timetable_detail_ids = request.POST.getlist('result_timetable_detail_id[]')
            result_timetable_detail_ids_for_delete = request.POST.getlist('result_timetable_detail_id-for-delete[]')
            assignment_id = request.POST.get('assignment_id')
        
            # Ensure data validation for the remaining operations
            if not (course_ids and result_identification_ids and instructor_ids and class_group_ids and meeting_days and start_times and end_times):
                messages.info(request, 'No data has been saved.')
                return redirect(request.get_full_path())
        
            with transaction.atomic():
                # Create or retrieve the main ResultTimetable entry
                result_identification = get_object_or_404(ResultIdentification, result_id=result_identification_ids[0])
                instructor = get_object_or_404(User, id=instructor_ids[0])
                class_group_id = class_group_ids[0]
                course_id = course_ids[0]
        
                if timetable_result_ids:
                    # Use the first timetable_result_id to update the existing entry
                    result_timetable_id = timetable_result_ids[0]
                    result_timetable = get_object_or_404(ResultTimetable, result_id=result_timetable_id)
                    result_timetable.result_identification = result_identification
                    result_timetable.instructor = instructor
                    result_timetable.class_group_id = class_group_id
                    result_timetable.course_id = course_id
                    result_timetable.save()
                else:
                    # Create a new ResultTimetable entry
                    result_timetable, created = ResultTimetable.objects.get_or_create(
                        result_identification=result_identification,
                        instructor=instructor,
                        class_group_id=class_group_id,
                        course_id=course_id
                    )
        
                # Loop to process details
                for i in range(len(course_ids)):
                    classroom_id = classroom_ids[i]
                    meeting_day = meeting_days[i]
                    start_time = start_times[i]
                    end_time = end_times[i]
                    is_online_class = is_online_classes[i].lower() == 'online'
                    result_timetable_detail_id = result_timetable_detail_ids[i] if i < len(result_timetable_detail_ids) and result_timetable_detail_ids[i] else None
        
                    # Get the last meeting ID and increment it
                    last_meeting = ResultMeetingTime.objects.filter(result_identification=result_identification).order_by('-meeting_id').first()
                    new_meeting_id = last_meeting.meeting_id + 1 if last_meeting else 1
        
                    # Save the ResultMeetingTime object
                    ResultMeetingTime.objects.create(
                        result_identification=result_identification,
                        meeting_id=new_meeting_id,
                        meeting_day=meeting_day,
                        start_time=start_time,
                        end_time=end_time,
                        is_online_meeting=is_online_class
                    )
        
                    if result_timetable_detail_id:
                        # Update existing ResultTimetableDetail
                        result_timetable_detail = get_object_or_404(ResultTimetableDetail, result_id=result_timetable_detail_id)
                        result_timetable_detail.result_identification = result_identification
                        result_timetable_detail.room_id = classroom_id if not is_online_class else None
                        result_timetable_detail.meeting_id = new_meeting_id
                        result_timetable_detail.result_timetable = result_timetable
                        result_timetable_detail.save()
                    else:
                        # Avoid duplicate ResultTimetableDetail entries
                        if not ResultTimetableDetail.objects.filter(
                            result_identification=result_identification,
                            room_id=classroom_id if not is_online_class else None,
                            meeting_id=new_meeting_id,
                            result_timetable=result_timetable
                        ).exists():
                            ResultTimetableDetail.objects.create(
                                result_identification=result_identification,
                                room_id=classroom_id if not is_online_class else None,
                                meeting_id=new_meeting_id,
                                result_timetable=result_timetable
                            )
        
                # Delete ResultTimetable entries with no associated ResultTimetableDetail entries
                empty_timetables = ResultTimetable.objects.annotate(detail_count=Count('details')).filter(detail_count=0)
                empty_timetables.delete()
        
                # Clean up initial assignments
                if assignment_id:
                    InitialCourseAssignment.objects.filter(assignment_id=assignment_id).delete()
        
                # Delete timetable details based on IDs without fetching result_identification
                if result_timetable_detail_ids_for_delete:
                    ResultTimetableDetail.objects.filter(result_id__in=result_timetable_detail_ids_for_delete).delete()
        
            messages.success(request, 'Schedule has been saved successfully.')
            return redirect(request.get_full_path())
        
        raise Http404
    
      
    

    message_displayed = False
    for assignment in assignments:
        for item in instructor_timetable_data['instructor_timetable']:
            if assignment['course_id__course_id'] == item['course_id']:
                message_displayed = True
                break
        if message_displayed:
            break

    combined_total_units = instructor_timetable_data['total_units'] + total_unit_assignments
    if combined_total_units > 18:
        warnings.append("Instructor is overloaded with schedules.")
    if template and request.user.user_type == 4:
        
        if "generate_pdf" in request.GET:
          return redirect(reverse('generate_pdf', args=[result_identification, selected_instructor_id]))

        return render(request, template, {
            'days': get_weekdays.get_ordered_weekdays(),
            'periods': get_periods.get_ordered_periods(),
            'result_identification': result_identification,
            'selected_classroom_id': selected_classroom_id,
            'selected_classroom_type': selected_classroom_type,
            'selected_year_level': selected_year_level,
            'selected_class_group_id': selected_class_group_id,
            'instructors': list(instructor_query),
            'selected_instructor_id': selected_instructor_id,
            'selected_instructor': selected_instructor, 
            **instructor_timetable_data,
            **instructor_list,
            'is_shared': is_shared,
            **conflicts_data,
            'assignments': assignments,
            'combined_total_units': combined_total_units,
            'view_mode': view_mode,
             'warnings': warnings,
             'message_displayed': message_displayed,
        })
    raise Http404