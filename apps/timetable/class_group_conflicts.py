from datetime import datetime

def parse_time(time_str):
    return datetime.strptime(time_str.strip(), "%I:%M %p").time()

def detect_class_group_conflicts(class_group_timetable):
    conflicts = []
    infos = []
    warnings = []
    conflicts_set = set()
    warnings_set = set()
    infos_set = set()
    total_conflicts = 0
    total_warnings = 0
    total_infos = 0
    conflicting_ids = set()
    no_schedule_ids = set()
    no_instructor_ids = set()

    for i, entry1 in enumerate(class_group_timetable):
        course_name_1 = entry1.get('course_code')
        room_1 = entry1.get('room_name')
        meeting_day_1 = entry1.get('meeting_day', '').split(', ')
        meeting_time_1 = entry1.get('meeting_time', '').strip()
        instructor_name_1 = entry1.get('instructor_name', '')
        flexible_day_1 = entry1.get('flexible_day', '')
        is_online_1 = 'ONLINE' in entry1.get('schedule', [])
        no_instructor_ids = list({entry['result_timetable_detail_id'] for entry in class_group_timetable if not entry.get('instructor_id')})
        no_schedule_ids = set()
        for entry in class_group_timetable:
            is_online = entry.get('is_online_class', False)
            room_name = entry.get('room_name', '').strip()
            if not entry.get('meeting_time') or not entry.get('meeting_day') or (not room_name and not is_online):
                no_schedule_ids.add(entry['result_timetable_detail_id'])
        no_schedule_ids = list(no_schedule_ids)

        if not instructor_name_1:
            info_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}'
            info_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned instructor.'
                f'</button>'
            )
            if info_message_key not in infos_set:
                infos_set.add(info_message_key)
                infos.append(info_message)
                total_infos += 1

        if not meeting_day_1 and not meeting_time_1 and not room_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_time_day_room'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned time, day, and room.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
            continue

        if not meeting_day_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_days'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned days.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1

        if not meeting_time_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_time'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned time.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1

        if not room_1 and not flexible_day_1 and not is_online_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_classroom'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned classroom.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1

        if meeting_time_1 and '-' in meeting_time_1:
            start_time_1, end_time_1 = meeting_time_1.split('-')
            start_time_1 = parse_time(start_time_1)
            end_time_1 = parse_time(end_time_1)
        else:
            if meeting_time_1:
                warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-invalid_time'
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-class-group" '
                    f'data-result-identification="{entry1["result_identification"]}" '
                    f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                    f'data-instructor-id="{entry1["instructor_id"]}" '
                    f'data-course-code="{entry1["course_code"]}" '
                    f'data-classroom-id="{entry1["room_id"]}" '
                    f'data-start-time="{entry1["start_time"]}" '
                    f'data-end-time="{entry1["end_time"]}" '
                    f'data-meeting-day="{entry1["meeting_day"]}">'
                    f'{course_name_1} has an invalid time format.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
            continue

        if not instructor_name_1:
            info_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}'
            info_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned instructor.'
                f'</button>'
            )
            if info_message_key not in infos_set:
                infos_set.add(info_message_key)
                infos.append(info_message)
                total_infos += 1
        
        if not meeting_day_1 and not meeting_time_1 and not room_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_time_day_room'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned time, day, and room.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
            continue
        
        if not meeting_day_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_days'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned days.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
        
        if not meeting_time_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_time'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned time.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
        
        if not room_1 and not flexible_day_1 and not is_online_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_classroom'
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-class-group" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-course-code="{entry1["course_code"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{course_name_1} has no assigned classroom.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
        
        if meeting_time_1 and '-' in meeting_time_1:
            start_time_1, end_time_1 = meeting_time_1.split('-')
            start_time_1 = parse_time(start_time_1)
            end_time_1 = parse_time(end_time_1)
        else:
            if meeting_time_1:
                warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-invalid_time'
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-class-group" '
                    f'data-result-identification="{entry1["result_identification"]}" '
                    f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                    f'data-instructor-id="{entry1["instructor_id"]}" '
                    f'data-course-code="{entry1["course_code"]}" '
                    f'data-classroom-id="{entry1["room_id"]}" '
                    f'data-start-time="{entry1["start_time"]}" '
                    f'data-end-time="{entry1["end_time"]}" '
                    f'data-meeting-day="{entry1["meeting_day"]}">'
                    f'{course_name_1} has an invalid time format.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
            continue
        
        for j in range(i + 1, len(class_group_timetable)):
            entry2 = class_group_timetable[j]
            course_name_2 = entry2.get('course_code')
            room_2 = entry2.get('room_name')
            meeting_day_2 = entry2.get('f2f_day', '').split(', ')
            meeting_time_2 = entry2.get('meeting_time', '').strip()
            flexible_day_2 = entry2.get('flexible_day', '')
            is_online_2 = 'ONLINE' in entry2.get('schedule', [])
        
            if not meeting_day_2 and not meeting_time_2 and not room_2:
                warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_time_day_room'
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-class-group" '
                    f'data-result-identification="{entry2["result_identification"]}" '
                    f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry2["result_timetable_detail_id"]}" '
                    f'data-instructor-id="{entry2["instructor_id"]}" '
                    f'data-course-code="{entry2["course_code"]}" '
                    f'data-classroom-id="{entry2["room_id"]}" '
                    f'data-start-time="{entry2["start_time"]}" '
                    f'data-end-time="{entry2["end_time"]}" '
                    f'data-meeting-day="{entry2["meeting_day"]}">'
                    f'{course_name_2} has no assigned time, day, and room.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
                continue
        
            if not meeting_day_2:
                warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_days'
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-class-group" '
                    f'data-result-identification="{entry2["result_identification"]}" '
                    f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry2["result_timetable_detail_id"]}" '
                    f'data-instructor-id="{entry2["instructor_id"]}" '
                    f'data-course-code="{entry2["course_code"]}" '
                    f'data-classroom-id="{entry2["room_id"]}" '
                    f'data-start-time="{entry2["start_time"]}" '
                    f'data-end-time="{entry2["end_time"]}" '
                    f'data-meeting-day="{entry2["meeting_day"]}">'
                    f'{course_name_2} has no assigned days.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
        
            if not meeting_time_2:
                warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_time'
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-class-group" '
                    f'data-result-identification="{entry2["result_identification"]}" '
                    f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry2["result_timetable_detail_id"]}" '
                    f'data-instructor-id="{entry2["instructor_id"]}" '
                    f'data-course-code="{entry2["course_code"]}" '
                    f'data-classroom-id="{entry2["room_id"]}" '
                    f'data-start-time="{entry2["start_time"]}" '
                    f'data-end-time="{entry2["end_time"]}" '
                    f'data-meeting-day="{entry2["meeting_day"]}">'
                    f'{course_name_2} has no assigned time.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
        
            if not room_2 and not flexible_day_2 and not is_online_2:
                warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_classroom'
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-class-group" '
                    f'data-result-identification="{entry2["result_identification"]}" '
                    f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry2["result_timetable_detail_id"]}" '
                    f'data-instructor-id="{entry2["instructor_id"]}" '
                    f'data-course-code="{entry2["course_code"]}" '
                    f'data-classroom-id="{entry2["room_id"]}" '
                    f'data-start-time="{entry2["start_time"]}" '
                    f'data-end-time="{entry2["end_time"]}" '
                    f'data-meeting-day="{entry2["meeting_day"]}">'
                    f'{course_name_2} has no assigned classroom.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
        
            if meeting_time_2 and '-' in meeting_time_2:
                start_time_2, end_time_2 = meeting_time_2.split('-')
                start_time_2 = parse_time(start_time_2)
                end_time_2 = parse_time(end_time_2)
            else:
                if meeting_time_2:
                    warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-invalid_time'
                    warning_message = (
                        f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                        f'data-hs-overlay="#assign-schedule-class-group" '
                        f'data-result-identification="{entry2["result_identification"]}" '
                        f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                        f'data-timetable-result-detail-id="{entry2["result_timetable_detail_id"]}" '
                        f'data-instructor-id="{entry2["instructor_id"]}" '
                        f'data-course-code="{entry2["course_code"]}" '
                        f'data-classroom-id="{entry2["room_id"]}" '
                        f'data-start-time="{entry2["start_time"]}" '
                        f'data-end-time="{entry2["end_time"]}" '
                        f'data-meeting-day="{entry2["meeting_day"]}">'
                        f'{course_name_2} has an invalid time format.'
                        f'</button>'
                    )
                    if warning_message_key not in warnings_set:
                        warnings_set.add(warning_message_key)
                        warnings.append(warning_message)
                        total_warnings += 1
                continue

            overlapping_days = set(meeting_day_1) & set(meeting_day_2)
            if overlapping_days:
                if start_time_1 < end_time_2 and start_time_2 < end_time_1:
                    conflicting_ids.update([entry1["result_timetable_detail_id"], entry2["result_timetable_detail_id"]])
                    conflict_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-{",".join(sorted(set(meeting_day_1 + meeting_day_2)))}'
                    days = ', '.join(sorted(set(meeting_day_1 + meeting_day_2)))
                    class_group_name = entry1.get('class_group_name', 'None')
                    if room_1 and room_2:
                        conflict_message = (
                            f'<span class="font-semibold uppercase"> {class_group_name} - {days}:  </span>'
                            f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                            f'data-hs-overlay="#assign-schedule-class-group" '
                            f'data-result-identification="{entry1["result_identification"]}" '
                            f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                            f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                            f'data-instructor-id="{entry1["instructor_id"]}" '
                            f'data-course-code="{entry1["course_code"]}" '
                            f'data-classroom-id="{entry1["room_id"]}" '
                            f'data-start-time="{entry1["start_time"]}" '
                            f'data-end-time="{entry1["end_time"]}" '
                            f'data-meeting-day="{entry1["meeting_day"]}">'
                            f"{course_name_1} in {room_1} with time {start_time_1.strftime('%I:%M %p')} - {end_time_1.strftime('%I:%M %p')}"
                            f'</button> and '
                            f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                            f'data-hs-overlay="#assign-schedule-class-group" '
                            f'data-result-identification="{entry2["result_identification"]}" '
                            f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                            f'data-timetable-result-detail-id="{entry2["result_timetable_detail_id"]}" '
                            f'data-instructor-id="{entry2["instructor_id"]}" '
                            f'data-course-code="{entry2["course_code"]}" '
                            f'data-classroom-id="{entry2["room_id"]}" '
                            f'data-start-time="{entry2["start_time"]}" '
                            f'data-end-time="{entry2["end_time"]}" '
                            f'data-meeting-day="{entry2["meeting_day"]}">'
                            f"{course_name_2} in {room_2} with time {start_time_2.strftime('%I:%M %p')} - {end_time_2.strftime('%I:%M %p')}"
                            f'</button>.'
                        )
                    elif room_1:
                        conflict_message = (
                            f'<span class="font-semibold uppercase"> {class_group_name} - {days}:  </span>'
                            f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                            f'data-hs-overlay="#assign-schedule-class-group" '
                            f'data-result-identification="{entry1["result_identification"]}" '
                            f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                            f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                            f'data-instructor-id="{entry1["instructor_id"]}" '
                            f'data-course-code="{entry1["course_code"]}" '
                            f'data-classroom-id="{entry1["room_id"]}" '
                            f'data-start-time="{entry1["start_time"]}" '
                            f'data-end-time="{entry1["end_time"]}" '
                            f'data-meeting-day="{entry1["meeting_day"]}">'
                            f"{course_name_1} in {room_1} with time {start_time_1.strftime('%I:%M %p')} - {end_time_1.strftime('%I:%M %p')}"
                            f'</button> and '
                            f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                            f'data-hs-overlay="#assign-schedule-class-group" '
                            f'data-result-identification="{entry2["result_identification"]}" '
                            f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                            f'data-timetable-result-detail-id="{entry2["result_timetable_detail_id"]}" '
                            f'data-instructor-id="{entry2["instructor_id"]}" '
                            f'data-course-code="{entry2["course_code"]}" '
                            f'data-classroom-id="{entry2["room_id"]}" '
                            f'data-start-time="{entry2["start_time"]}" '
                            f'data-end-time="{entry2["end_time"]}" '
                            f'data-meeting-day="{entry2["meeting_day"]}">'
                            f"{course_name_2} with time {start_time_2.strftime('%I:%M %p')} - {end_time_2.strftime('%I:%M %p')}"
                            f'</button>.'
                        )
                    elif room_2:
                        conflict_message = (
                            f'<span class="font-semibold uppercase"> {class_group_name} - {days}:  </span>'
                            f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                            f'data-hs-overlay="#assign-schedule-class-group" '
                            f'data-result-identification="{entry1["result_identification"]}" '
                            f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                            f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                            f'data-instructor-id="{entry1["instructor_id"]}" '
                            f'data-course-code="{entry1["course_code"]}" '
                            f'data-classroom-id="{entry1["room_id"]}" '
                            f'data-start-time="{entry1["start_time"]}" '
                            f'data-end-time="{entry1["end_time"]}" '
                            f'data-meeting-day="{entry1["meeting_day"]}">'
                            f"{course_name_1} with time {start_time_1.strftime('%I:%M %p')} - {end_time_1.strftime('%I:%M %p')}"
                            f'</button> and '
                            f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                            f'data-hs-overlay="#assign-schedule-class-group" '
                            f'data-result-identification="{entry2["result_identification"]}" '
                            f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                            f'data-timetable-result-detail-id="{entry2["result_timetable_detail_id"]}" '
                            f'data-instructor-id="{entry2["instructor_id"]}" '
                            f'data-course-code="{entry2["course_code"]}" '
                            f'data-classroom-id="{entry2["room_id"]}" '
                            f'data-start-time="{entry2["start_time"]}" '
                            f'data-end-time="{entry2["end_time"]}" '
                            f'data-meeting-day="{entry2["meeting_day"]}">'
                            f"{course_name_2} in {room_2} with time {start_time_2.strftime('%I:%M %p')} - {end_time_2.strftime('%I:%M %p')}"
                            f'</button>.'
                        )
                    else:
                        conflict_message = (
                            f'<span class="font-semibold uppercase"> {class_group_name} - {days}:  </span>'
                            f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                            f'data-hs-overlay="#assign-schedule-class-group" '
                            f'data-result-identification="{entry1["result_identification"]}" '
                            f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                            f'data-timetable-result-detail-id="{entry1["result_timetable_detail_id"]}" '
                            f'data-instructor-id="{entry1["instructor_id"]}" '
                            f'data-course-code="{entry1["course_code"]}" '
                            f'data-classroom-id="{entry1["room_id"]}" '
                            f'data-start-time="{entry1["start_time"]}" '
                            f'data-end-time="{entry1["end_time"]}" '
                            f'data-meeting-day="{entry1["meeting_day"]}">'
                            f"{course_name_1} with time {start_time_1.strftime('%I:%M %p')} - {end_time_1.strftime('%I:%M %p')} "
                            f'</button> and '
                            f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                            f'data-hs-overlay="#assign-schedule-class-group" '
                            f'data-result-identification="{entry2["result_identification"]}" '
                            f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                            f'data-timetable-result-detail-id="{entry2["result_timetable_detail_id"]}" '
                            f'data-instructor-id="{entry2["instructor_id"]}" '
                            f'data-course-code="{entry2["course_code"]}" '
                            f'data-classroom-id="{entry2["room_id"]}" '
                            f'data-start-time="{entry2["start_time"]}" '
                            f'data-end-time="{entry2["end_time"]}" '
                            f'data-meeting-day="{entry2["meeting_day"]}">'
                            f"{course_name_2} with time {start_time_2.strftime('%I:%M %p')} - {end_time_2.strftime('%I:%M %p')}."
                            f'</button>.'
                        )
                    if conflict_message_key not in conflicts_set:
                        conflicts_set.add(conflict_message_key)
                        conflicts.append(conflict_message)
                        total_conflicts += 1
                        
    return {'total_conflicts': total_conflicts, 'conflicts': conflicts, 'total_warnings': total_warnings, 'warnings': warnings, 'total_infos': total_infos, 'infos': infos, 'conflicting_ids': conflicting_ids, 'no_instructor_ids': list(no_instructor_ids), 'no_schedule_ids': no_schedule_ids}

def detect_all_class_group_conflicts(class_group_timetable, class_group_id):
    conflicts = []
    infos = []
    warnings = []
    conflicts_set = set()
    warnings_set = set()
    infos_set = set()
    total_conflicts = 0
    total_warnings = 0
    total_infos = 0

    # Filter entries by the specified class group ID
    entries = [entry for entry in class_group_timetable if entry.get('class_group_id') == class_group_id]

    for i, entry1 in enumerate(entries):
        course_name_1 = entry1.get('course_code')
        room_1 = entry1.get('room_name')
        meeting_day_1 = entry1.get('meeting_day', '').split(', ')
        meeting_time_1 = entry1.get('meeting_time', '').strip()
        instructor_name_1 = entry1.get('instructor_name', '')
        flexible_day_1 = entry1.get('flexible_day', '')
        is_online_1 = 'ONLINE' in entry1.get('schedule', '')
        class_group_name_1 = entry1.get('class_group_name', 'Unknown Group')

        if not instructor_name_1:
            info_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}'
            info_message = (
                f'<a href="/timetable/scheduler/classgroups/{entry1["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                f'<span class="font-semibold uppercase"> {class_group_name_1} - {course_name_1}:  </span>'
                f'No instructor has been assigned.'
                f'</a>'
            )
            if info_message_key not in infos_set:
                infos_set.add(info_message_key)
                infos.append(info_message)
                total_infos += 1

        if not meeting_day_1 and not meeting_time_1 and not room_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_time_day_room'
            warning_message = (
                f'<a href="/timetable/scheduler/classgroups/{entry1["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                f'<span class="font-semibold uppercase"> {class_group_name_1} - {course_name_1}:  </span>'
                f'No time, day, and room have been assigned.'
                f'</a>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
            continue

        if not meeting_day_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_days'
            warning_message = (
                f'<a href="/timetable/scheduler/classgroups/{entry1["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                f'<span class="font-semibold uppercase"> {class_group_name_1} - {course_name_1}:  </span>'
                f'No days have been assigned.'
                f'</a>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1

        if not meeting_time_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_time'
            warning_message = (
                f'<a href="/timetable/scheduler/classgroups/{entry1["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                f'<span class="font-semibold uppercase"> {class_group_name_1} - {course_name_1}:  </span>'
                f'No time has been assigned.'
                f'</a>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1

        if not room_1 and not flexible_day_1 and not is_online_1:
            warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-no_classroom'
            warning_message = (
                f'<a href="/timetable/scheduler/classgroups/{entry1["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                f'<span class="font-semibold uppercase"> {class_group_name_1} - {course_name_1}:  </span>'
                f'No classroom has been assigned.'
                f'</a>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1

        if meeting_time_1 and '-' in meeting_time_1:
            start_time_1, end_time_1 = meeting_time_1.split('-')
            start_time_1 = parse_time(start_time_1)
            end_time_1 = parse_time(end_time_1)
        else:
            if meeting_time_1:
                warning_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-invalid_time'
                warning_message = (
                    f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                    f'<span class="font-semibold uppercase"> {class_group_name_1} - {course_name_1}:  </span>'
                    f'Invalid time format.'
                    f'</a>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
            continue

        for j in range(i + 1, len(entries)):
            entry2 = entries[j]
            course_name_2 = entry2.get('course_code')
            room_2 = entry2.get('room_name')
            meeting_day_2 = entry2.get('meeting_day', '').split(', ')
            meeting_time_2 = entry2.get('meeting_time', '').strip()
            flexible_day_2 = entry2.get('flexible_day', '')
            is_online_2 = 'ONLINE' in entry2.get('schedule', '')
            class_group_name_2 = entry2.get('class_group_name', 'Unknown Group')

            if not meeting_day_2 and not meeting_time_2 and not room_2:
                warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_time_day_room'
                warning_message = (
                    f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                    f'<span class="font-semibold uppercase"> {class_group_name_2} - {course_name_2}:  </span>'
                    f'No time, day, and room have been assigned.'
                    f'</a>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
                continue

            if not meeting_day_2:
                warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_days'
                warning_message = (
                    f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                    f'<span class="font-semibold uppercase"> {class_group_name_2} - {course_name_2}:  </span>'
                    f'No days have been assigned.'
                    f'</a>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1

            if not meeting_time_2:
                warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_time'
                warning_message = (
                    f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                    f'<span class="font-semibold uppercase"> {class_group_name_2} - {course_name_2}:  </span>'
                    f'No time has been assigned.'
                    f'</a>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1

            if not room_2 and not flexible_day_2 and not is_online_2:
                warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-no_classroom'
                warning_message = (
                    f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                    f'<span class="font-semibold uppercase"> {class_group_name_2} - {course_name_2}:  </span>'
                    f'No classroom has been assigned.'
                    f'</a>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1

            if meeting_time_2 and '-' in meeting_time_2:
                start_time_2, end_time_2 = meeting_time_2.split('-')
                start_time_2 = parse_time(start_time_2)
                end_time_2 = parse_time(end_time_2)
            else:
                if meeting_time_2:
                    warning_message_key = f'{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}-invalid_time'
                    warning_message = (
                        f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                        f'<span class="font-semibold uppercase"> {class_group_name_2} - {course_name_2}:  </span>'
                        f'Invalid time format.'
                        f'</a>'
                    )
                    if warning_message_key not in warnings_set:
                        warnings_set.add(warning_message_key)
                        warnings.append(warning_message)
                        total_warnings += 1
                continue

            overlapping_days = set(meeting_day_1) & set(meeting_day_2)
            if overlapping_days:
                if start_time_1 < end_time_2 and start_time_2 < end_time_1:
                    conflict_message_key = f'{course_name_1}-{entry1["result_identification"]}-{entry1["timetable_result_id"]}-{course_name_2}-{entry2["result_identification"]}-{entry2["timetable_result_id"]}'
                    day = ', '.join(overlapping_days)
                    class_group_name = entry1.get('class_group_name', 'Unknown Group')
                    if room_1 and room_2:
                        conflict_message = (
                            f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                            f'<span class="font-semibold uppercase"> {class_group_name} - {day}:  </span>'
                            f"{course_name_1} in {room_1} from {start_time_1.strftime('%I:%M %p')} to {end_time_1.strftime('%I:%M %p')} "
                            f'and '
                            f"{course_name_2} in {room_2} from {start_time_2.strftime('%I:%M %p')} to {end_time_2.strftime('%I:%M %p')}."
                            f'</a>'
                        )
                    elif room_1:
                        conflict_message = (
                            f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                            f'<span class="font-semibold uppercase"> {class_group_name} - {day}:  </span>'
                            f"{course_name_1} in {room_1} from {start_time_1.strftime('%I:%M %p')} to {end_time_1.strftime('%I:%M %p')} "
                            f'and '
                            f"{course_name_2} from {start_time_2.strftime('%I:%M %p')} to {end_time_2.strftime('%I:%M %p')}."
                            f'</a>'
                        )
                    elif room_2:
                        conflict_message = (
                            f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                            f'<span class="font-semibold uppercase"> {class_group_name} - {day}:  </span>'
                            f"{course_name_1} from {start_time_1.strftime('%I:%M %p')} to {end_time_1.strftime('%I:%M %p')} "
                            f'and '
                            f"{course_name_2} in {room_2} from {start_time_2.strftime('%I:%M %p')} to {end_time_2.strftime('%I:%M %p')}."
                            f'</a>'
                        )
                    else:
                        conflict_message = (
                            f'<a href="/timetable/scheduler/classgroups/{entry2["result_identification"]}/?class_group_id={class_group_id}&year_level=all" class="timetable-entry hover:underline focus:outline-none focus:underline">'
                            f'<span class="font-semibold uppercase"> {class_group_name} - {day}:  </span>'
                            f"{course_name_1} from {start_time_1.strftime('%I:%M %p')} to {end_time_1.strftime('%I:%M %p')} "
                            f'and '
                            f"{course_name_2} from {start_time_2.strftime('%I:%M %p')} to {end_time_2.strftime('%I:%M %p')}."
                            f'</a>'
                        )
                    if conflict_message_key not in conflicts_set:
                        conflicts_set.add(conflict_message_key)
                        conflicts.append(conflict_message)
                        total_conflicts += 1
                        print(f"Conflict detected in class group {class_group_id}: {conflict_message}")

    return {'total_conflicts': total_conflicts, 'conflicts': conflicts, 'total_warnings': total_warnings, 'warnings': warnings, 'total_infos': total_infos, 'infos': infos}