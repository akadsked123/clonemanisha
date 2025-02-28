import json
import random
from apps.algorithm.class_group import ClassGroup
from apps.algorithm.classroom import Classroom
from apps.algorithm.course import Course
from apps.algorithm.instructor import Instructor
from apps.algorithm.meeting_time import MeetingTime, RoomMeetingTime
from apps.algorithm.program import Program

class Data:
    @staticmethod
    def load_data(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        institute = data.get('institute', {})
        programs = []
        courses = []
        class_groups = []
        meeting_times = []
        year_levels = {}
        unique_ids = set()

        def generate_unique_class_group_id(year_level, i):
            while True:
                unique_number = random.randint(100, 999)
                class_group_id = f"G{year_level}{unique_number:03}"
                if class_group_id not in unique_ids:
                    unique_ids.add(class_group_id)
                    return class_group_id
                
        instructors = [
            Instructor(
                id=f"I{int(instructor['instructor_id']):04}",
                name=instructor['instructor_name'],
                courses=instructor.get('courses', []),
                availability=instructor.get('availability', [])
            ) for instructor in institute.get('instructors', [])
        ]
        
        classrooms = [
            Classroom(
                id=f"R{classroom['room_id']:04}",
                roomName=classroom['room_name'],
                is_lab=classroom['is_lab']
            ) for classroom in institute.get('classrooms', [])
        ]

        meeting_times = [
            MeetingTime(
                id=f"{meeting['meeting_id']:04}",
                time=meeting['meeting_time'],
                creditHour=meeting['credit_hours'],
                conflictingTimes=meeting['conflicts'],
                roomConflictingTimes=meeting['room_conflicts']
            ) for meeting in institute.get('timetable', [])
        ]

        room_meeting_times = [
            RoomMeetingTime(
                id=f"{meeting['meeting_id']:04}",
                time=meeting['meeting_time'],
                creditHour=meeting['credit_hours'],
                conflictingTimes=meeting['conflicts']
            ) for meeting in institute.get('classroom_timetable', [])
        ]

        for program in institute.get('programs', []):
            program_courses = []
            for level in program.get('course_levels', []):
                year_level = level['year_level']
                number_of_classes = level['number_of_classes']

                class_group_list = []
                for i in range(number_of_classes):
                    program_code = program['program_code']
                    class_group_id = generate_unique_class_group_id(year_level, i)
                    class_group_name = f"{program_code} {year_level}{chr(65 + i)}"
                    class_group = ClassGroup(id=class_group_id, name=class_group_name, year_level=year_level)
                    class_groups.append(class_group)
                    class_group_list.append(class_group)

                for course in level.get('courses', []):
                    course_id = f"C{int(course['course_id']):04}"
                    new_course = Course(
                        id=course_id,
                        program=program['program_id'],
                        course_code=course['course_code'],
                        course_description=course['course_description'],
                        lecture_hours=course['lecture_hours'],
                        laboratory_hours=course['laboratory_hours'],
                        creditHour=course['credit_units'],
                        instructors=[
                          instructor for instructor in instructors
                          if any(course['course_id'] == c['course_id'] for c in instructor.get_courses())
                        ],
                        year_level=year_level
                    )
                    courses.append(new_course)
                    program_courses.append(new_course)
                    for class_group in class_group_list:
                        class_group._scheduleCourses.append(new_course)

                if year_level not in year_levels:
                    year_levels[year_level] = []
                year_levels[year_level].extend(class_group_list)

            new_program = Program(
                id=program['program_id'],
                name=program['program_name'],
                program_code=program['program_code'],
                courses=program_courses
            )
            programs.append(new_program)

        return {
            'instructors': instructors,
            'classrooms': classrooms,
            'courses': courses,
            'programs': programs,
            'class_groups': class_groups,
            'meeting_times': meeting_times,
            'room_meeting_times' : room_meeting_times,
            'year_levels': year_levels
        }