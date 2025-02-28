from datetime import datetime, timedelta

def get_vacant_times(classroom_timetable, days):
    # Define the start and end times
    start_time = datetime.strptime("07:00 AM", "%I:%M %p")
    end_time = datetime.strptime("08:00 PM", "%I:%M %p")
    time_interval = timedelta(minutes=30)

    # Generate all possible time slots, excluding lunch break
    all_time_slots = []
    current_time = start_time
    while current_time < end_time:
        next_time = current_time + time_interval
        if not (current_time.time() == datetime.strptime("12:00 PM", "%I:%M %p").time() or
                current_time.time() == datetime.strptime("12:30 PM", "%I:%M %p").time()):
            all_time_slots.append((current_time.time(), next_time.time()))
        current_time = next_time

    # Initialize the vacant times dictionary
    vacant_times = {day: all_time_slots.copy() for day in days}

    # Mark occupied time slots
    for entry in classroom_timetable:
        entry_days = entry['meeting_day'].split(', ')
        occupied_time = entry.get('meeting_time', '').strip()
        
        if occupied_time and '-' in occupied_time:
            start, end = occupied_time.split('-')
            start = datetime.strptime(start.strip(), "%I:%M %p").time()
            end = datetime.strptime(end.strip(), "%I:%M %p").time()

            for day in entry_days:
                day = day.strip()
                if day in vacant_times:
                    vacant_times[day] = [slot for slot in vacant_times[day] if not (start <= slot[0] < end or start < slot[1] <= end)]
                else:
                    print(f"Warning: Day '{day}' not found in the list of days")
        else:
            print(f"Warning: Occupied time '{occupied_time}' is not correctly formatted or is empty")

    # Format the vacant times for output, excluding lunch break
    formatted_vacant_times = {}
    for day, slots in vacant_times.items():
        formatted_vacant_times[day] = [f"{slot[0].strftime('%I:%M %p')} - {slot[1].strftime('%I:%M %p')}" for slot in slots]

    return formatted_vacant_times

def get_vacant_time_slots(classroom_timetable, days):
    # Define the start and end times
    start_time = datetime.strptime("07:00 AM", "%I:%M %p")
    end_time = datetime.strptime("08:00 PM", "%I:%M %p")
    time_interval = timedelta(minutes=30)

    # Generate all possible time slots, excluding lunch break
    all_time_slots = []
    current_time = start_time
    while current_time < end_time:
        next_time = current_time + time_interval
        if not (current_time.time() == datetime.strptime("12:00 PM", "%I:%M %p").time() or
                current_time.time() == datetime.strptime("12:30 PM", "%I:%M %p").time()):
            all_time_slots.append((current_time.time(), next_time.time()))
        current_time = next_time

    # Initialize the vacant times dictionary
    vacant_times = {day: all_time_slots.copy() for day in days}

    # Mark occupied time slots
    for entry in classroom_timetable:
        entry_days = entry['f2f_day'].split(', ')
        occupied_time = entry.get('meeting_time', '').strip()
        
        if occupied_time and '-' in occupied_time:
            start, end = occupied_time.split('-')
            start = datetime.strptime(start.strip(), "%I:%M %p").time()
            end = datetime.strptime(end.strip(), "%I:%M %p").time()

            for day in entry_days:
                day = day.strip()
                if day in vacant_times:
                    vacant_times[day] = [slot for slot in vacant_times[day] if not (start <= slot[0] < end or start < slot[1] <= end)]
                else:
                    print(f"Warning: Day '{day}' not found in the list of days")
        else:
            print(f"Warning: Occupied time '{occupied_time}' is not correctly formatted or is empty")

    # Format the vacant times for output, merging consecutive slots
    formatted_vacant_times = {}
    for day, slots in vacant_times.items():
        merged_slots = []
        if slots:
            start = slots[0][0]
            end = slots[0][1]
            for i in range(1, len(slots)):
                if slots[i][0] == end:
                    end = slots[i][1]
                else:
                    merged_slots.append((start, end))
                    start = slots[i][0]
                    end = slots[i][1]
            merged_slots.append((start, end))
        
        formatted_vacant_times[day] = [f"{slot[0].strftime('%I:%M %p')} to {slot[1].strftime('%I:%M %p')}" for slot in merged_slots]

    return formatted_vacant_times