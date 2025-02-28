from apps.timetable.models import ResultClassroom

def get_selected_classroom(request, result_identification):
    selected_classroom_type = request.GET.get('classroom_type', request.session.get('selected_classroom_type', 'all'))
    selected_classroom_id = request.GET.get('classroom_id') or request.session.get('selected_classroom_id')

    if request.session.get('result_identification') != result_identification:
        request.session.pop('selected_classroom_id', None)
        request.session['result_identification'] = result_identification
        selected_classroom_id = None

    if selected_classroom_id:
        if not ResultClassroom.objects.filter(result_identification=result_identification, room_id=selected_classroom_id).exists():
            selected_classroom_id = None
            request.session.pop('selected_classroom_id', None)
        else:
            request.session['selected_classroom_id'] = selected_classroom_id
    else:
        selected_classroom_id = request.session.get('selected_classroom_id')
        if not selected_classroom_id or not ResultClassroom.objects.filter(result_identification=result_identification, room_id=selected_classroom_id).exists():
            first_classroom = ResultClassroom.objects.filter(result_identification=result_identification).order_by('room_id').first()
            if first_classroom:
                selected_classroom_id = first_classroom.room_id
                request.session['selected_classroom_id'] = selected_classroom_id

    request.session['selected_classroom_type'] = selected_classroom_type

    return selected_classroom_type, selected_classroom_id