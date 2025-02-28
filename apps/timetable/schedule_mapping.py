from datetime import datetime

schedule_mapping = [
    {"Code": "M*WF", "Days": "Wednesday, Friday", "Online": "Monday"},
    {"Code": "MW*F", "Days": "Monday, Friday", "Online": "Wednesday"},
    {"Code": "MWF*", "Days": "Monday, Wednesday", "Online": "Friday"},
    {"Code": "T*TH", "Days": "Thursday", "Online": "Tuesday"},
    {"Code": "TTH*", "Days": "Tuesday", "Online": "Thursday"},
    {"Code": "WF*_", "Days": "Wednesday", "Online": "Friday"},
    {"Code": "M*W_", "Days": "Wednesday", "Online": "Monday"},
    {"Code": "MW*_", "Days": "Monday", "Online": "Wednesday"},
    {"Code": "FRI_", "Days": None, "Online": "Friday"},
    {"Code": "MON_", "Days": None, "Online": "Monday"},
    {"Code": "TUE_", "Days": None , "Online": "Tuesday"},
    {"Code": "WED_", "Days": None, "Online":"Wednesday"},
    {"Code": "THU_", "Days": None, "Online": "Thursday"}, 
     {"Code": "SAT_", "Days": None, "Online": "Saturday"}, 
     {"Code": "SUN_", "Days": None, "Online": "Sunday"}, 
    {"Code": "MW_", "Days": "Monday, Wednesday", "Online": None},
    {"Code": "MW*", "Days": "Monday", "Online": "Wednesday"},
    {"Code": "TTH", "Days": "Tuesday, Thursday", "Online": None},
    {"Code": "W*F_", "Days": "Friday", "Online": "Wednesday"},
    {"Code": "M*F_", "Days": "Friday", "Online": "Monday"},
    {"Code": "WF_", "Days": "Wednesday, Friday", "Online": None},
    {"Code": "WF*", "Days": "Wednesday", "Online": "Friday"},
    {"Code": "MF_", "Days": "Monday, Friday", "Online": None},
    {"Code": "M*TTH", "Days": "Tuesday, Thursday", "Online": "Monday"},
    {"Code": "MT*TH", "Days": "Monday, Thursday", "Online": "Tuesday"},
    {"Code": "MTTH*", "Days": "Monday, Tuesday", "Online": "Thursday"},
    {"Code": "T*THF", "Days": "Thursday, Friday", "Online": "Tuesday"},
    {"Code": "TTH*F", "Days": "Tuesday, Friday", "Online": "Thursday"},
    {"Code": "TTHF*", "Days": "Tuesday, Thursday", "Online": "Friday"},
    {"Code": "T*THM", "Days": "Thursday, Monday", "Online": "Tuesday"},
    {"Code": "TTH*M", "Days": "Tuesday, Monday", "Online": "Thursday"},
    {"Code": "TTHM*", "Days": "Tuesday, Thursday", "Online": "Monday"},
    {"Code": "W*TTH", "Days": "Tuesday, Thursday", "Online": "Wednesday"},
    {"Code": "WT*TH", "Days": "Wednesday, Thursday", "Online": "Tuesday"},
    {"Code": "WTTH*", "Days": "Wednesday, Tuesday", "Online": "Thursday"}
]


day_order = {
    'Monday': 1,
    'Tuesday': 2,
    'Wednesday': 3,
    'Thursday': 4,
    'Friday': 5,
    'Saturday': 6,
    'Sunday': 7
}

def get_year_levels():
    return [
        {'year_level': 1, 'name': 'First Year'},
        {'year_level': 2, 'name': 'Second Year'},
        {'year_level': 3, 'name': 'Third Year'},
        {'year_level': 4, 'name': 'Fourth Year'},
    ]

def combine_and_sort_days(schedule_details):
    days = schedule_details.get('Days', '')
    online = schedule_details.get('Online', '')

    # Ensure days and online are not None before splitting
    days_list = days.split(',') if days else []
    online_list = online.split(',') if online else []

    combined_days = list(set(days_list + online_list))
    sorted_days = sorted(combined_days, key=lambda day: day_order.get(day.strip(), 0))
    return ', '.join(sorted_days)

def split_days(schedule_details):
    days = schedule_details.get('Days', '')
    online = schedule_details.get('Online', '')

    days_list = days.split(',') if days else []
    online_list = online.split(',') if online else []

    return days_list + online_list

def format_time_12_hour(time_str):
    if time_str:
        try:
            time_obj = datetime.strptime(time_str, '%H:%M:%S')
            return time_obj.strftime('%I:%M %p')
        except ValueError:
            return time_str
    return time_str

def get_schedule_details(meeting_time):
    if not meeting_time:
        return None

    try:
        code, time_range = meeting_time.split(' ', 1)
    except ValueError:
        return None

    for entry in schedule_mapping:
        if entry["Code"] == code:
            start_time, end_time = time_range.split(' - ')
            start_time_24 = f"{start_time}:00"
            end_time_24 = f"{end_time}:00"

            try:
                start_time_obj = datetime.strptime(start_time_24, '%H:%M:%S')
                formatted_start_time = start_time_obj.strftime('%I:%M %p')
            except ValueError:
                formatted_start_time = start_time_24

            try:
                end_time_obj = datetime.strptime(end_time_24, '%H:%M:%S')
                formatted_end_time = end_time_obj.strftime('%I:%M %p')
            except ValueError:
                formatted_end_time = end_time_24

            schedule_details = {
                "Days": entry["Days"],
                "Online": entry["Online"],
                "Time": f"{formatted_start_time} - {formatted_end_time}"
            }
            return schedule_details
    return None