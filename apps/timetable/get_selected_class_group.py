from apps.timetable.models import ResultClassGroup

def get_selected_class_group(request, result_identification):
    selected_year_level = request.GET.get('year_level', request.session.get('selected_year_level', 'all'))
    selected_class_group_id = request.GET.get('class_group_id')

    if request.session.get('result_identification') != result_identification:
        request.session.pop('selected_class_group_id', None)
        request.session['result_identification'] = result_identification

    if selected_year_level != 'all':
        try:
            selected_year_level = int(selected_year_level)
            if selected_year_level not in [1, 2, 3, 4]:
                selected_year_level = 'all'
        except ValueError:
            selected_year_level = 'all'
    request.session['selected_year_level'] = selected_year_level

    if selected_class_group_id:
        if not ResultClassGroup.objects.filter(result_identification=result_identification, class_group_id=selected_class_group_id).exists():
            selected_class_group_id = None
            request.session.pop('selected_class_group_id', None)
        else:
            request.session['selected_class_group_id'] = selected_class_group_id
    else:
        selected_class_group_id = request.session.get('selected_class_group_id')
        if not selected_class_group_id or not ResultClassGroup.objects.filter(result_identification=result_identification, class_group_id=selected_class_group_id).exists():
            if selected_year_level == 'all':
                first_class_group = ResultClassGroup.objects.filter(result_identification=result_identification).order_by('class_group_name').first()
            else:
                first_class_group = ResultClassGroup.objects.filter(result_identification=result_identification, year_level=selected_year_level).order_by('class_group_name').first()
            if first_class_group:
                selected_class_group_id = first_class_group.class_group_id
                request.session['selected_class_group_id'] = selected_class_group_id

    return selected_year_level, selected_class_group_id