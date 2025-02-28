from datetime import datetime
from apps.user.models import User
# Detect instructor conflicts in the timetable per instructor
def detect_instructor_conflicts(instructor_timetable, additional_warnings=None, additional_total_warnings=0):
    conflicts = []
    warnings = []
    warnings_set = set(additional_warnings) if additional_warnings else set()
    total_conflicts = 0
    conflicts_set = set()
    total_warnings = additional_total_warnings
    conflicting_ids = set()
    no_schedule_or_room_ids = set()
    n = len(instructor_timetable)

    for i in range(n):
        entry1 = instructor_timetable[i]
        days1 = entry1.get('schedule', [])
        class_group_name1 = entry1.get('class_group_name', 'N/A')

        if not days1:
            no_schedule_or_room_ids.add(entry1["timetable_result_detail_id"])
            warning_message_key = f"{entry1['course_code']}-{entry1['result_identification']}-{entry1['timetable_result_id']}-no_schedule"
            warning_message = (
                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                f'data-hs-overlay="#assign-schedule-instructor" '
                f'data-result-identification="{entry1["result_identification"]}" '
                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                f'data-timetable-result-detail-id="{entry1["timetable_result_detail_id"]}" '
                f'data-instructor-id="{entry1["instructor_id"]}" '
                f'data-classroom-id="{entry1["room_id"]}" '
                f'data-start-time="{entry1["start_time"]}" '
                f'data-end-time="{entry1["end_time"]}" '
                f'data-meeting-day="{entry1["meeting_day"]}">'
                f'{entry1["course_code"]} ({class_group_name1}) has no assigned schedule.'
                f'</button>'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
            continue

        for schedule1 in days1:
            room1, day1, time1 = schedule1.split(', ')
            if time1 and '-' in time1:
                start1, end1 = time1.split(' - ')
                start1 = datetime.strptime(start1.strip(), "%I:%M %p")
                end1 = datetime.strptime(end1.strip(), "%I:%M %p")
            else:
                continue

            if room1 != "ONLINE" and not room1:
                no_schedule_or_room_ids.add(entry1["timetable_result_detail_id"])
                warning_message_key = f"{entry1['course_code']}-{entry1['result_identification']}-{entry1['timetable_result_id']}-no_room"
                warning_message = (
                    f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                    f'data-hs-overlay="#assign-schedule-instructor" '
                    f'data-result-identification="{entry1["result_identification"]}" '
                    f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                    f'data-timetable-result-detail-id="{entry1["timetable_result_detail_id"]}" '
                    f'data-instructor-id="{entry1["instructor_id"]}" '
                    f'data-classroom-id="{entry1["room_id"]}" '
                    f'data-start-time="{entry1["start_time"]}" '
                    f'data-end-time="{entry1["end_time"]}" '
                    f'data-meeting-day="{entry1["meeting_day"]}">'
                    f'{entry1["course_code"]} ({class_group_name1}) has no assigned room.'
                    f'</button>'
                )
                if warning_message_key not in warnings_set:
                    warnings_set.add(warning_message_key)
                    warnings.append(warning_message)
                    total_warnings += 1
                continue

            for j in range(i + 1, n):
                entry2 = instructor_timetable[j]
                days2 = entry2.get('schedule', [])
                class_group_name2 = entry2.get('class_group_name', 'N/A')

                if not days2:
                    no_schedule_or_room_ids.add(entry2["timetable_result_detail_id"])
                    warning_message_key = f"{entry2['course_code']}-{entry2['result_identification']}-{entry2['timetable_result_id']}-no_schedule"
                    warning_message = (
                        f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                        f'data-hs-overlay="#assign-schedule-instructor" '
                        f'data-result-identification="{entry2["result_identification"]}" '
                        f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                        f'data-timetable-result-detail-id="{entry2["timetable_result_detail_id"]}" '
                        f'data-instructor-id="{entry2["instructor_id"]}" '
                        f'data-classroom-id="{entry2["room_id"]}" '
                        f'data-start-time="{entry2["start_time"]}" '
                        f'data-end-time="{entry2["end_time"]}" '
                        f'data-meeting-day="{entry2["meeting_day"]}">'
                        f'{entry2["course_code"]} ({class_group_name2}) has no assigned schedule.'
                        f'</button>'
                    )
                    if warning_message_key not in warnings_set:
                        warnings_set.add(warning_message_key)
                        warnings.append(warning_message)
                        total_warnings += 1
                    continue

                for schedule2 in days2:
                    room2, day2, time2 = schedule2.split(', ')
                    if time2 and '-' in time2:
                        start2, end2 = time2.split(' - ')
                        start2 = datetime.strptime(start2.strip(), "%I:%M %p")
                        end2 = datetime.strptime(end2.strip(), "%I:%M %p")
                    else:
                        continue

                    if day1 == day2:
                        if start1 < end2 and start2 < end1:
                            conflict_message_key = f"{entry1['course_code']}-{entry1['result_identification']}-{entry1['timetable_result_id']}-{entry2['course_code']}-{entry2['result_identification']}-{entry2['timetable_result_id']}"
                            conflict_message = (
                                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                                f'data-hs-overlay="#assign-schedule-instructor" '
                                f'data-result-identification="{entry1["result_identification"]}" '
                                f'data-timetable-result-id="{entry1["timetable_result_id"]}" '
                                f'data-timetable-result-detail-id="{entry1["timetable_result_detail_id"]}" '
                                f'data-instructor-id="{entry1["instructor_id"]}" '
                                f'data-classroom-id="{entry1["room_id"]}" '
                                f'data-start-time="{entry1["start_time"]}" '
                                f'data-end-time="{entry1["end_time"]}" '
                                f'data-meeting-day="{entry1["meeting_day"]}">'
                                f'{entry1["course_code"]} ({class_group_name1}) on {day1} from {start1.strftime("%I:%M %p")} to {end1.strftime("%I:%M %p")}'
                                f'</button> and '
                                f'<button class="timetable-entry hover:underline focus:outline-none focus:underline" '
                                f'data-hs-overlay="#assign-schedule-instructor" '
                                f'data-result-identification="{entry2["result_identification"]}" '
                                f'data-timetable-result-id="{entry2["timetable_result_id"]}" '
                                f'data-timetable-result-detail-id="{entry2["timetable_result_detail_id"]}" '
                                f'data-instructor-id="{entry2["instructor_id"]}" '
                                f'data-classroom-id="{entry2["room_id"]}" '
                                f'data-start-time="{entry2["start_time"]}" '
                                f'data-end-time="{entry2["end_time"]}" '
                                f'data-meeting-day="{entry2["meeting_day"]}">'
                                f'{entry2["course_code"]} ({class_group_name2}) on {day2} from {start2.strftime("%I:%M %p")} to {end2.strftime("%I:%M %p")}'
                                f'</button>.'
                            )
                            if conflict_message_key not in conflicts_set:
                                conflicts_set.add(conflict_message_key)
                                conflicts.append(conflict_message)
                                total_conflicts += 1
                                conflicting_ids.update([entry1["timetable_result_detail_id"], entry2["timetable_result_detail_id"]])
                                
    return {'total_conflicts': total_conflicts, 'conflicts': conflicts, 'total_warnings': total_warnings, 'warnings': warnings, 'conflicting_ids': list(conflicting_ids), 'no_schedule_or_room_ids': list(no_schedule_or_room_ids)}




def get_instructor_by_id(instructor_id):
    try:
        instructor = User.objects.get(id=instructor_id)
        return instructor
    except User.DoesNotExist:
        return None

def detect_all_instructor_conflicts(request, instructor_timetable, additional_warnings=None, additional_total_warnings=0):
    conflicts = []
    warnings = []
    warnings_set = set(additional_warnings) if additional_warnings else set()
    total_conflicts = 0
    conflicts_set = set()
    total_warnings = additional_total_warnings

    # Group entries by instructor
    timetable_by_instructor = {}
    for entry in instructor_timetable:
        instructor_id = entry.get('instructor_id')
        if not instructor_id:
            continue  # Skip entries with no instructor_id

        days = entry.get('schedule', [])
        class_group_name = entry.get('class_group_name', 'N/A')

        if not days:
            warning_message_key = f"{entry['course_code']}-{entry['result_identification']}-{entry['timetable_result_id']}-no_schedule"
            warning_message = (
                f'{entry["course_code"]} ({class_group_name}) has no assigned schedule.'
            )
            if warning_message_key not in warnings_set:
                warnings_set.add(warning_message_key)
                warnings.append(warning_message)
                total_warnings += 1
            continue

        for schedule in days:
            room, day, time = schedule.split(', ')
            if time and '-' in time:
                start, end = time.split(' - ')
                start = datetime.strptime(start.strip(), "%I:%M %p")
                end = datetime.strptime(end.strip(), "%I:%M %p")
            else:
                continue

            if instructor_id not in timetable_by_instructor:
                timetable_by_instructor[instructor_id] = {}
            if day not in timetable_by_instructor[instructor_id]:
                timetable_by_instructor[instructor_id][day] = []
            timetable_by_instructor[instructor_id][day].append({'start': start, 'end': end, 'entry': entry, 'room': room})

    # Check for conflicts within each instructor's timetable
    for instructor_id, timetable in timetable_by_instructor.items():
        instructor = get_instructor_by_id(instructor_id)
        if not instructor:
            continue  # Skip if instructor not found
        instructor_full_name = f"{instructor.first_name} {instructor.middle_name or ''} {instructor.last_name}".strip()
        for day, entries in timetable.items():
            entries.sort(key=lambda x: x['start'])
            for i in range(len(entries) - 1):
                start1, end1, entry1, room1 = entries[i]['start'], entries[i]['end'], entries[i]['entry'], entries[i]['room']
                start2, end2, entry2, room2 = entries[i + 1]['start'], entries[i + 1]['end'], entries[i + 1]['entry'], entries[i + 1]['room']

                if start1 < end2 and start2 < end1:
                    conflict_message_key = f"{entry1['course_code']}-{entry1['result_identification']}-{entry1['timetable_result_id']}-{entry2['course_code']}-{entry2['result_identification']}-{entry2['timetable_result_id']}"
                    conflict_message = (
                        f'<span class="font-semibold uppercase"> {instructor_full_name}:  </span>'
                        f'<a href="/timetable/scheduler/instructors/{entry1["result_identification"]}/?instructor_id={entry1["instructor_id"]}" class="hover:underline focus:outline-none focus:underline">'
                        f'{entry1["course_code"]} ({entry1.get("class_group_name", "N/A")}) on {day} from {start1.strftime("%I:%M %p")} to {end1.strftime("%I:%M %p")} '
                        f'and '
                        f'{entry2["course_code"]} ({entry2.get("class_group_name", "N/A")}) on {day} from {start2.strftime("%I:%M %p")} to {end2.strftime("%I:%M %p")}'
                        f'</a>.'
                    )
                    if conflict_message_key not in conflicts_set:
                        conflicts_set.add(conflict_message_key)
                        conflicts.append(conflict_message)
                        total_conflicts += 1

    return {'total_conflicts': total_conflicts, 'conflicts': conflicts, 'total_warnings': total_warnings, 'warnings': warnings}