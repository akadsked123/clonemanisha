from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from apps.timetable.models import ResultIdentification, ResultMeetingTime, ResultTimetable, ResultTimetableDetail
from apps.user.models import User
from django.contrib import messages
from django.db import transaction

def create_timetable_form(request, result_identification):
    if request.method == 'POST' and 'CreateTimetableSubmit' in request.POST:
        instructor_id = request.POST.get('instructor_id')
        course_id = request.POST.get('course_id')
        class_group_id = request.POST.get('class_group_id')
        classroom_id = request.POST.get('classroom_id')
        meeting_day = request.POST.get('meeting_day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_online_class = request.POST.get('learning-mode')

        print("====================================CREATE TIMETABLE====================================")
        print("instructor_id: ", instructor_id)
        print("course_id: ", course_id)
        print("class_group_id: ", class_group_id)
        print("classroom_id: ", classroom_id)
        print("meeting_day: ", meeting_day)
        print("start_time: ", start_time)
        print("end_time: ", end_time)
        print("result_identification: ", result_identification)
        print("is_online_class: ", is_online_class)

        # Validate that required fields are not empty
        if (not classroom_id and not is_online_class) or not meeting_day or not start_time or not end_time:
            messages.info(request, "Fill out all required fields.")
            return redirect(request.get_full_path())

        # Convert fields to integers if they are not empty
        try:
            instructor_id = int(instructor_id) if instructor_id else None
            course_id = int(course_id) if course_id else None
            class_group_id = int(class_group_id) if class_group_id else None
            classroom_id = int(classroom_id) if classroom_id else None
        except ValueError:
            messages.error(request, "Invalid input for numeric fields.")
            return redirect(request.get_full_path())

        # Fetch the ResultIdentification instance
        result_identification_instance = get_object_or_404(ResultIdentification, pk=result_identification)

        with transaction.atomic():
            # Check if a ResultTimetable entry already exists
            result_timetable = ResultTimetable.objects.filter(
                result_identification=result_identification_instance,
                course_id=course_id,
                class_group_id=class_group_id
            ).first()

            if not result_timetable:
                # Create a new ResultTimetable entry if it doesn't exist
                result_timetable = ResultTimetable.objects.create(
                    result_identification=result_identification_instance,
                    course_id=course_id,
                    class_group_id=class_group_id,
                    instructor_id=instructor_id
                )

            # Create a new ResultMeetingTime entry
            last_meeting = ResultMeetingTime.objects.filter(result_identification=result_timetable.result_identification).order_by('-meeting_id').first()
            new_meeting_id = last_meeting.meeting_id + 1 if last_meeting else 1
            result_meeting_time = ResultMeetingTime.objects.create(
                result_identification=result_timetable.result_identification,
                meeting_id=new_meeting_id,
                meeting_day=meeting_day,
                start_time=start_time,
                end_time=end_time,
                is_online_meeting=is_online_class if is_online_class else 0
            )

            # Create a new ResultTimetableDetail entry
            ResultTimetableDetail.objects.create(
                result_identification=result_timetable.result_identification,
                result_timetable=result_timetable,
                room_id=classroom_id,
                meeting_id=result_meeting_time.meeting_id
            )
        messages.success(request, 'Schedule has been created successfully.')

        return HttpResponseRedirect(request.path_info)

# def create_timetable_form(request, result_identification):
#     if request.method == 'POST' and 'CreateTimetableSubmit' in request.POST:
#         instructor_id = request.POST.get('instructor_id')
#         course_id = request.POST.get('course_id')
#         class_group_id = request.POST.get('class_group_id')
#         classroom_id = request.POST.get('classroom_id')
#         meeting_day = request.POST.get('meeting_day')
#         start_time = request.POST.get('start_time')
#         end_time = request.POST.get('end_time')
#         is_online_class = request.POST.get('learning-mode')

#         # Validate that required fields are not empty
#         if (not classroom_id and not is_online_class) or not meeting_day or not start_time or not end_time:
#             messages.info(request, "Fill out all required fields.")
#             return redirect(request.get_full_path())

#         # Convert fields to integers if they are not empty
#         try:
#             instructor_id = int(instructor_id) if instructor_id else None
#             course_id = int(course_id) if course_id else None
#             class_group_id = int(class_group_id) if class_group_id else None
#             classroom_id = int(classroom_id) if classroom_id else None
#         except ValueError:
#             messages.error(request, "Invalid input for numeric fields.")
#             return redirect(request.get_full_path())

#         # Fetch the ResultIdentification instance
#         result_identification_instance = get_object_or_404(ResultIdentification, pk=result_identification)

#         with transaction.atomic():
#             # Create a new ResultTimetable entry
#             result_timetable = ResultTimetable.objects.create(
#                 result_identification=result_identification_instance,
#                 course_id=course_id,
#                 class_group_id=class_group_id,
#                 instructor_id=instructor_id
#             )

#             # Create a new ResultMeetingTime entry
#             last_meeting = ResultMeetingTime.objects.filter(result_identification=result_timetable.result_identification).order_by('-meeting_id').first()
#             new_meeting_id = last_meeting.meeting_id + 1 if last_meeting else 1
#             result_meeting_time = ResultMeetingTime.objects.create(
#               result_identification=result_timetable.result_identification,
#               meeting_id=new_meeting_id,
#               meeting_day=meeting_day,
#               start_time=start_time,
#               end_time=end_time,
#               is_online_meeting=is_online_class if is_online_class else 0
#             )

#             # Create a new ResultTimetableDetail entry
#             ResultTimetableDetail.objects.create(
#                 result_identification=result_timetable.result_identification,
#                 result_timetable=result_timetable,
#                 room_id=classroom_id,
#                 meeting_id=result_meeting_time.meeting_id
#             )
#         messages.success(request, 'Schedule has been created successfully.')

#         return HttpResponseRedirect(request.path_info)