from apps.timetable.models import ResultInstructor

def get_selected_instructor(request, result_identification):
    selected_instructor_id = request.GET.get('instructor_id')
    
    if request.session.get('result_identification') != result_identification:
        request.session.pop('selected_instructor_id', None)
        request.session['result_identification'] = result_identification
    
    if selected_instructor_id:
        instructor_exists = ResultInstructor.objects.filter(result_identification=result_identification, instructor_id=selected_instructor_id).exists()
        if instructor_exists:
            request.session['selected_instructor_id'] = selected_instructor_id
        else:
            selected_instructor_id = None
    else:
        selected_instructor_id = request.session.get('selected_instructor_id')
    
    if not selected_instructor_id:
        first_instructor = ResultInstructor.objects.filter(result_identification=result_identification).order_by('instructor_name').first()
        if first_instructor:
            selected_instructor_id = first_instructor.instructor_id
            request.session['selected_instructor_id'] = selected_instructor_id
    
    return selected_instructor_id