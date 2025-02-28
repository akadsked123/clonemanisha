from prettytable import PrettyTable

def display_initial_data(data):
    # Print ClassGroup
    class_group_table = PrettyTable()
    class_group_table.field_names = ["Id", "Name", "Courses"]

    for class_group in data['class_groups']:
        class_group_table.add_row([class_group.get_id(), class_group.get_name(), class_group.get_scheduleCourses()])

    print("Class Group")
    print(class_group_table)
    print(f"Total Class Groups: {len(data['class_groups'])}")

    # Print Instructor
    instructor_table = PrettyTable()
    instructor_table.field_names = ["Id", "Name"]

    for instructor in data['instructors']:
        instructor_table.add_row([instructor.get_id(), instructor.get_name()])

    print("\nInstructor")
    print(instructor_table)
    print(f"Total Instructors: {len(data['instructors'])}")

    # Print Classroom
    classroom_table = PrettyTable()
    classroom_table.field_names = ["Id","Name", "Is lab?"]

    for classroom in data['classrooms']:
        classroom_table.add_row([classroom.get_id(), classroom.get_roomName(), "Yes" if classroom.get_is_lab() else "No"])

    print(f"\nClassroom")
    print(classroom_table)
    print(f"Total Classrooms: {len(data['classrooms'])}")

    # Print Program
    program_table = PrettyTable()
    program_table.field_names = ["Name", "Total", "Courses" ]

    for program in data['programs']:
        program_table.add_row([program.get_name(), len(program.get_courses()), program.get_courses()])

    print("\nProgram")
    print(program_table)
    print(f"Total Programs: {len(data['programs'])}")

    # Print Course
    course_table = PrettyTable()
    course_table.field_names = ["Id", "Program", "Code", "Description", "Lecture Hours", "Lab Hours", "Credit Hour", "Instructors"]

    for course in data['courses']:
        course_table.add_row([course.get_id(), course.get_program(), course.get_course_code(), course.get_course_description(), course.get_lecture_hours(), course.get_laboratory_hours(), course.get_creditHour(), course.get_instructors()])

    print("\nCourse")
    print(course_table)
    print(f"Total Courses: {len(data['courses'])}")

    timetable = PrettyTable()
    timetable.field_names = ["Id", "Meeting time", "Credit Hour", "Conflicting Time"]

    for meeting_time in data['meeting_times']:
        timetable.add_row([
            meeting_time.get_id(),
            meeting_time.get_time(),
            meeting_time.get_creditHour(),
            meeting_time.get_conflictingTimes()
        ])

    print("\nTimeTable")
    print(timetable)
    print(f"Total Meeting Times: {len(data['meeting_times'])}")
