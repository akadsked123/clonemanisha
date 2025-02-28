
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from apps.timetable.models import ResultMeetingTime, ResultTimetable, ResultTimetableDetail
from apps.user.models import User
from django.contrib import messages
from django.db import transaction

def update_timetable_form(request):
    if request.method == 'POST' and 'UpdateTimetableSubmit' in request.POST:
        timetable_result_id = request.POST.get('timetable-result-id')
        selected_instructor_id = request.POST.get('selected_instructor')
        classroom_id = request.POST.get('selected_classroom')
        meeting_day = request.POST.get('meeting_day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_online_class = request.POST.get('learning-mode')
        result_timetable_detail_id = request.POST.get('timetable-detail-result-id')

        # Validate that required fields are not empty
        if (not classroom_id and not is_online_class) or not meeting_day or not start_time or not end_time:
            messages.info(request, "Fill out all required fields.")
            return redirect(request.get_full_path())

        # Convert fields to integers if they are not empty
        try:
            timetable_result_id = int(timetable_result_id) if timetable_result_id else None
            selected_instructor_id = int(selected_instructor_id) if selected_instructor_id else None
            classroom_id = int(classroom_id) if classroom_id else None
            result_timetable_detail_id = int(result_timetable_detail_id) if result_timetable_detail_id else None
        except ValueError:
            messages.error(request, "Invalid input for numeric fields.")
            return redirect(request.get_full_path())

        with transaction.atomic():
            # Retrieve the main ResultTimetable entry
            result_timetable = get_object_or_404(ResultTimetable, result_id=timetable_result_id)
            if selected_instructor_id:
                instructor = get_object_or_404(User, id=selected_instructor_id)
                result_timetable.instructor = instructor
            else:
                result_timetable.instructor = None
                messages.info(request, 'No instructor has been assigned.')
            result_timetable.save()

            # Create a new ResultMeetingTime entry
            last_meeting = ResultMeetingTime.objects.filter(result_identification=result_timetable.result_identification).order_by('-meeting_id').first()
            new_meeting_id = last_meeting.meeting_id + 1 if last_meeting else 1
            result_meeting_time = ResultMeetingTime.objects.create(
                result_identification=result_timetable.result_identification,
                meeting_id=new_meeting_id,
                meeting_day=meeting_day,
                start_time=start_time,
                end_time=end_time,
                is_online_meeting=is_online_class
            )

            # Update or create ResultTimetableDetail
            if result_timetable_detail_id:
                result_timetable_detail = get_object_or_404(ResultTimetableDetail, result_id=result_timetable_detail_id)
                result_timetable_detail.room_id = classroom_id
                result_timetable_detail.meeting_id = result_meeting_time.meeting_id
                result_timetable_detail.result_timetable = result_timetable
                result_timetable_detail.save()

        messages.success(request, 'Schedule has been saved successfully.')

        return HttpResponseRedirect(request.path_info)