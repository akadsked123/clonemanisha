from datetime import datetime

def detect_classroom_conflicts(classroom_timetable):
    conflicts = []
    warnings = []
    warnings_set = set()
    conflicts_set = set()
    total_conflicts = 0
    total_warnings = 0
    n = len(classroom_timetable)
    conflicting_ids = set()

    for i in range(n):
        entry1 = classroom_timetable[i]
        days1 = entry1.get('f2f_day', '').split(', ')
        time1 = entry1.get('meeting_time', '').strip()
        class_group_name1 = entry1.get('class_group_name', 'N/A')
    
        if not days1 and not time1:
            warning_message_key = f'{entry1["course_code"]}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_time_day'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-classroom" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["timetable_result_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-class-group-name="{entry1["class_group_name"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{entry1["course_code"]} ({class_group_name1}) has no assigned time and day.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
            continue
        elif not days1 or not time1:
            warning_message_key = f'{entry1["course_code"]}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_days_or_time'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-classroom" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["timetable_result_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-class-group-name="{entry1["class_group_name"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{entry1["course_code"]} ({class_group_name1}) has no assigned days or time.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
            continue
    
        if time1 and '-' in time1:
            start1, end1 = time1.split('-')
            start1 = datetime.strptime(start1.strip(), "%I:%M %p")
            end1 = datetime.strptime(end1.strip(), "%I:%M %p")
        else:
            continue

        for j in range(i + 1, n):
            entry2 = classroom_timetable[j]
            days2 = entry2.get('f2f_day', '').split(', ')
            time2 = entry2.get('meeting_time', '').strip()
            class_group_name2 = entry2.get('class_group_name', 'N/A')
        
            if not days2 and not time2:
                warning_message_key = f'{entry2["course_code"]}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_time_day'
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-classroom" '
                    f'data-result-identification="{entry2["result_identification"]}" '
                    f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry2["timetable_result_detail_id"]}" '
                    f'data-instructor-id="{entry2["instructor_id"]}" '
                     f'data-course-code="{entry2["course_code"]}" '
                     f'data-class-group-name="{entry2["class_group_name"]}" '
                    f'data-classroom-id="{entry2["room_id"]}" '
                    f'data-start-time="{entry2["start_time"]}" '
                    f'data-end-time="{entry2["end_time"]}" '
                    f'data-meeting-day="{entry2["meeting_day"]}">'
                    f'{entry2["course_code"]} ({class_group_name2}) has no assigned time and day.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
                continue
            elif not days2 or not time2:
                warning_message_key = f'{entry2["course_code"]}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_days_or_time'
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-classroom" '
                    f'data-result-identification="{entry2["result_identification"]}" '
                    f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry2["timetable_result_detail_id"]}" '
                    f'data-instructor-id="{entry2["instructor_id"]}" '
                     f'data-course-code="{entry2["course_code"]}" '
                     f'data-class-group-name="{entry2["class_group_name"]}" '
                    f'data-classroom-id="{entry2["room_id"]}" '
                    f'data-start-time="{entry2["start_time"]}" '
                    f'data-end-time="{entry2["end_time"]}" '
                    f'data-meeting-day="{entry2["meeting_day"]}">'
                    f'{entry2["course_code"]} ({class_group_name2}) has no assigned days or time.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
                continue
        
            if time2 and '-' in time2:
                start2, end2 = time2.split('-')
                start2 = datetime.strptime(start2.strip(), "%I:%M %p")
                end2 = datetime.strptime(end2.strip(), "%I:%M %p")
            else:
                warning_message_key = f'{entry2["course_code"]}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-invalid_time'
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-classroom" '
                    f'data-result-identification="{entry2["result_identification"]}" '
                    f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry2["timetable_result_detail_id"]}" '
                    f'data-instructor-id="{entry2["instructor_id"]}" '
                     f'data-course-code="{entry2["course_code"]}" '
                     f'data-class-group-name="{entry2["class_group_name"]}" '
                    f'data-classroom-id="{entry2["room_id"]}" '
                    f'data-start-time="{entry2["start_time"]}" '
                    f'data-end-time="{entry2["end_time"]}" '
                    f'data-meeting-day="{entry2["meeting_day"]}">'
                    f'{entry2["course_code"]} ({class_group_name2}) has an invalid time format.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
                continue
        
            overlapping_days = set(days1) & set(days2)
            if days1 and days2 and overlapping_days and '' not in overlapping_days:
                if start1 < end2 and start2 < end1:
                    conflict_message_key = f'{entry1["course_code"]}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-{entry2["course_code"]}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}'
                    conflict_message = (
                         f'<span class="font-semibold uppercase"> {', '.join(overlapping_days)}: </span>'
                        f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                        f'data-hs-overlay="#assign-schedule-classroom" '
                        f'data-result-identification="{entry1["result_identification"]}" '
                        f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                        f'data-timetable-result-detail-id="{entry1["timetable_result_detail_id"]}" '
                        f'data-instructor-id="{entry1["instructor_id"]}" '
                        f'data-course-code="{entry1["course_code"]}" '
                        f'data-class-group-name="{entry1["class_group_name"]}" '
                        f'data-classroom-id="{entry1["room_id"]}" '
                        f'data-start-time="{entry1["start_time"]}" '
                        f'data-end-time="{entry1["end_time"]}" '
                        f'data-meeting-day="{entry1["meeting_day"]}">'
                        f'{entry1["course_code"]} ({class_group_name1}) from {start1.strftime("%I:%M %p")} to {end1.strftime("%I:%M %p")}'
                        f'</button> and '
                        f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                        f'data-hs-overlay="#assign-schedule-classroom" '
                        f'data-result-identification="{entry2["result_identification"]}" '
                        f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                        f'data-timetable-result-detail-id="{entry2["timetable_result_detail_id"]}" '
                        f'data-instructor-id="{entry2["instructor_id"]}" '
                        f'data-course-code="{entry2["course_code"]}" '
                        f'data-class-group-name="{entry2["class_group_name"]}" '
                        f'data-classroom-id="{entry2["room_id"]}" '
                        f'data-start-time="{entry2["start_time"]}" '
                        f'data-end-time="{entry2["end_time"]}" '
                        f'data-meeting-day="{entry2["meeting_day"]}">'
                        f'{entry2["course_code"]} ({class_group_name2}) from {start2.strftime("%I:%M %p")} to {end2.strftime("%I:%M %p")}'
                        f'</button>.'
                    )
                    if conflict_message_key not in conflicts_set:
                        conflicts_set.add(conflict_message_key)
                        conflicts.append(conflict_message)
                        total_conflicts += 1
                        conflicting_ids.update([entry1["timetable_result_detail_id"], entry2["timetable_result_detail_id"]])
                        
    return {'total_conflicts': total_conflicts, 'conflicts': conflicts, 'total_warnings': total_warnings, 'warnings': warnings,  'conflicting_ids': list(conflicting_ids)}