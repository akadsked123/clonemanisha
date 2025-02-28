from apps.timetable.get_selected_class_group import get_selected_class_group
from apps.timetable.get_selected_classroom import get_selected_classroom
from apps.timetable.get_selected_instructor import get_selected_instructor
from apps.timetable.instructor_conflicts import detect_all_instructor_conflicts
from apps.timetable.models import ResultClassGroup
from apps.timetable.schedule_class_group import class_group_timetable
from apps.timetable.schedule_instructor import instructor_timetable_for_all_conflicts
from apps.timetable.class_group_conflicts import detect_all_class_group_conflicts
from apps.user.utils import get_template_by_user_type
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from concurrent.futures import ThreadPoolExecutor
from apps.timetable.schedule_instructor import get_view_mode 


@login_required
def list_of_conflicts_view(request, result_identification):
    view_mode = get_view_mode(request)
    template = get_template_by_user_type(request.user, 'list-of-conflicts')
    selected_instructor_id = get_selected_instructor(request, result_identification)
    selected_year_level, selected_class_group_id = get_selected_class_group(request, result_identification)
    selected_classroom_type, selected_classroom_id = get_selected_classroom(request, result_identification)
    class_group_ids = ResultClassGroup.objects.filter(result_identification=result_identification).values_list('class_group_id', flat=True)
    
    # Get instructor timetable data
    instructor_timetable_data = instructor_timetable_for_all_conflicts(result_identification)
    
    # Get class group timetable data for all class groups
    class_group_timetable_data = []
    for class_group_id in class_group_ids:
        timetable_data = class_group_timetable(class_group_id, result_identification)['class_group_timetable']
        class_group_timetable_data.extend(timetable_data)

    # Detect conflicts
    instructor_conflicts_data = detect_all_instructor_conflicts(request, instructor_timetable_data['instructor_timetable'])
    
    def detect_conflicts_for_class_group(class_group_id):
        entries = [entry for entry in class_group_timetable_data if isinstance(entry, dict) and entry.get('class_group_id') == class_group_id]
        return class_group_id, detect_all_class_group_conflicts(entries, class_group_id)
    
    with ThreadPoolExecutor() as executor:
        all_class_group_conflicts_data = dict(executor.map(detect_conflicts_for_class_group, class_group_ids))

    # Combine the conflicts data
    total_class_group_conflicts = sum(data['total_conflicts'] for data in all_class_group_conflicts_data.values())
    total_class_group_warnings = sum(data['total_warnings'] for data in all_class_group_conflicts_data.values())
    total_class_group_infos = sum(data['total_infos'] for data in all_class_group_conflicts_data.values())
    class_group_conflicts = [conflict for data in all_class_group_conflicts_data.values() for conflict in data['conflicts']]
    class_group_warnings = [warning for data in all_class_group_conflicts_data.values() for warning in data['warnings']]
    class_group_infos = [info for data in all_class_group_conflicts_data.values() for info in data['infos']]

    conflicts_data = {
        'total_conflicts': instructor_conflicts_data.get('total_conflicts', 0) + total_class_group_conflicts,
        'conflicts': instructor_conflicts_data.get('conflicts', []) + class_group_conflicts,
        'total_warnings': instructor_conflicts_data.get('total_warnings', 0) + total_class_group_warnings,
        'warnings': instructor_conflicts_data.get('warnings', []) + class_group_warnings,
        'total_infos': instructor_conflicts_data.get('total_infos', 0) + total_class_group_infos,
        'infos': instructor_conflicts_data.get('infos', []) + class_group_infos,
    }

    if template and request.user.user_type == 4:
        return render(request, template, {
            'selected_instructor_id': selected_instructor_id,
            'result_identification': result_identification,
            'selected_class_group_id': selected_class_group_id,
            'selected_classroom_id': selected_classroom_id,
            'selected_year_level': selected_year_level,
            'selected_classroom_type': selected_classroom_type,
            'conflicts': conflicts_data['conflicts'],
            'total_conflicts': conflicts_data['total_conflicts'],
            'warnings': conflicts_data['warnings'],
            'total_warnings': conflicts_data['total_warnings'],
            'view_mode': view_mode
        })
    else:
        return HttpResponse("Unauthorized", status=401)