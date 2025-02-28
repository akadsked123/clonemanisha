from abc import abstractmethod, ABC
from datetime import timedelta
import random as rnd
from enum import Enum
from prettytable import PrettyTable
from tqdm import tqdm
from apps.algorithm.course import Course
from apps.algorithm.class_set import Class
from apps.timetable.models import GeneratedSchedule, InitialSchedulerData, ResultClassGroup, ResultClassroom, ResultCourse, ResultIdentification, ResultInstructor, ResultMeetingTime, ResultProgram, ResultTimetable, ResultTimetableDetail
from apps.timetable.schedule_mapping import get_schedule_details, split_days
from apps.user.models import User
import time
from uuid import uuid4

from django.db import transaction

class Conflict(ABC):
    class ConflictType(Enum):
        NUMBER_OF_CLASS_GRPOUP = 1
        INSTRUCTOR_BOOKING = 2
        ROOM_BOOKING = 3
        INSTRUCTOR_AVAILABILITY = 4

    @abstractmethod
    def get_conflict(self): pass
    @abstractmethod
    def get_conflictType(self): pass

class InstructorAvailabilityConflict(Conflict):
    def __init__(self, conflictClass, instructor):
        self._instructor = instructor
        self._conflictClass = conflictClass
    def get_conflict(self):
        return "["+str(self._conflictClass)+"] where instructor "+ \
            self._instructor.get_id() + "meeting not in ["+\
                ','.join(str(x) for x in self._instructor.get_availability())+\
                "] instructor availability Meeting times"
    def get_conflictType(self): return Conflict.ConflictType.INSTRUCTOR_AVAILABILITY.name

class InstructorBookingConflict(Conflict):
    def __init__(self, conflictBetweenClasses, instructor):
        self._instructor = instructor
        self._conflictBetweenClasses = conflictBetweenClasses
    def get_conflict(self):
        return "["+str(" & ".join(map(str, self._conflictBetweenClasses)))+\
            "] where instrcutor "+ self._instructor.get_id() + " scheduled to teach " \
            "both classes at the same time or conflicting meeting times"
    def get_conflictType(self): return Conflict.ConflictType.INSTRUCTOR_BOOKING.name

class RoomBookingConflict(Conflict):
    def __init__(self, conflictBetweenClasses, room):
        self._room = room
        self._conflictBetweenClasses = conflictBetweenClasses
    def get_conflict(self):
        return "["+str(" & ".join(map(str, self._conflictBetweenClasses)))+\
            "] where room "+ self._room.get_id() + " is booked for both classes at the same time"
    def get_conflictType(self): return Conflict.ConflictType.ROOM_BOOKING.name

class ClassGroupBookingConflict(Conflict):
    def __init__(self, conflictBetweenClasses, classGroup):
        self._classGroup = classGroup
        self._conflictBetweenClasses = conflictBetweenClasses
    def get_conflict(self):
        return "Class Group "+ self._classGroup.get_id() + " " + self._name + " has more than one class scheduled at the same time"
    def get_conflictType(self): return Conflict.ConflictType.NUMBER_OF_CLASS_GROUP.name

class Schedule:
    class DisplayMode(Enum): VERBOSE = 1; MUTE = 2
    class RunMode(Enum): STANDALONE = 1; P2P = 2
    class instructorAvailabilityMode(Enum): ENABLED = 1; DISABLED = 2
    runMode = RunMode.STANDALONE
    DisplayMode = DisplayMode.MUTE
    instructorAvailabilityMode = instructorAvailabilityMode.ENABLED

    def __init__(self, data):
        self._data = data
        self._conflicts = []
        self._numOfConflicts = 0
        self._classes = []
        self._fitness = -1
        self._classNumb = 0
        self._isFitnessChanged = True

    def get_rooms(self):
        return self._data['classrooms']

    def get_classgroups(self):
        return self._data['class_groups']

    def get_classes(self):
        self._isFitnessChanged = True
        return self._classes

    def get_fitness(self):
        if self._isFitnessChanged:
            self._fitness = self.calculate_fitness()
            self._isFitnessChanged = False
        return self._fitness

    def get_numOfConflicts(self):
        return self._numOfConflicts

    def get_available_meeting_times(self, credit_hour):
        return [mt for mt in self._data['meeting_times'] if str(mt.get_creditHour()) == str(credit_hour)]

    def initialize(self):
        SPECIFIC_COURSE_MEETING_TIMES = {"C0012": "M0312","C0110": "M0312"}
        SPECIFIC_COUSE_IDS = ["C0012", "C0110", "C0127", "C0146", "C0147", "C0138", "C0048", "C0049", "C0013", "C0028", "C0111", "C0127"]
        instructor_load = {}
        for class_group in self.get_classgroups():
            courses = class_group.get_scheduleCourses()
            for course in courses:
                if isinstance(course, Course):
                    newClass = Class(self._classNumb, class_group, course)
                    self._classNumb += 1
                    credit_hour = course.get_lecture_hours() + (course.get_laboratory_hours() * 3)
                    available_meeting_times = self.get_available_meeting_times(credit_hour)
    
                    if course.get_instructors():
                        valid_instructors = [
                            instructor for instructor in course.get_instructors()
                            if instructor_load.get(instructor.get_id(), 0) + credit_hour <= 18
                        ]
                        if valid_instructors:
                            instructor = valid_instructors[rnd.randrange(len(valid_instructors))]
                            newClass.set_instructor(instructor)
                            instructor_load[instructor.get_id()] = instructor_load.get(instructor.get_id(), 0) + credit_hour
                        else:
                            newClass.set_instructor(None)
                    else:
                        newClass.set_instructor(None)

                    # Assign meeting time
                    if available_meeting_times:
                        newClass.set_meetingTime(available_meeting_times[rnd.randrange(len(available_meeting_times))])
                    else:
                        newClass.set_meetingTime(None)
                  
                    if course.get_id() in SPECIFIC_COURSE_MEETING_TIMES:
                        specific_meeting_time_id = SPECIFIC_COURSE_MEETING_TIMES[course.get_id()]
                        specific_meeting_time = next((mt for mt in self._data['meeting_times'] if mt.get_id() == specific_meeting_time_id), None)
                        newClass.set_meetingTime(specific_meeting_time)
    
                    # Ensure no room is assigned to specific courses
                    if course.get_id() in SPECIFIC_COUSE_IDS:
                        newClass.set_room(None)
                    else:
                        if newClass.get_meetingTime() is not None:
                            rooms = self.get_rooms()
                            if course.get_laboratory_hours() > 0:
                                lab_rooms = [room for room in rooms if room.get_is_lab()]
                                if lab_rooms:
                                    newClass.set_room(lab_rooms[rnd.randrange(len(lab_rooms))])
                                else:
                                    newClass.set_room(None)
                            else:
                                lecture_rooms = [room for room in rooms if not room.get_is_lab()]
                                if lecture_rooms:
                                    newClass.set_room(lecture_rooms[rnd.randrange(len(lecture_rooms))])
                                else:
                                    newClass.set_room(None)
                        else:
                            newClass.set_room(None)
                    
                    newClass.set_classGroup(class_group)
                    self._classes.append(newClass)
    
        return self

    def calculate_fitness(self):
        self._conflicts = []
        self._numOfConflicts = 0
        classes = self.get_classes()
        
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                # Check if a lab course is assigned to a lecture room
                if classes[i].get_course().get_laboratory_hours() > 0 and classes[i].get_room() is not None and not classes[i].get_room().get_is_lab():
                    self._conflicts.append(RoomBookingConflict(classes[i], classes[i].get_room()))
                    self._numOfConflicts += 1
                if classes[i].get_meetingTime() is not None and classes[j].get_meetingTime() is not None:
                    # Check for instructor booking conflicts
                    if (classes[i].get_meetingTime().get_id() == classes[j].get_meetingTime().get_id() or
                        classes[i].get_meetingTime().get_id() in classes[j].get_meetingTime().get_conflictingTimes()):
                        if classes[i].get_instructor() is not None and classes[j].get_instructor() is not None and \
                           classes[i].get_instructor().get_id() == classes[j].get_instructor().get_id():
                            instructorBookingConflict = [classes[i], classes[j]]
                            self._conflicts.append(InstructorBookingConflict(instructorBookingConflict, classes[j].get_instructor()))
                            self._numOfConflicts += 1
    
                    # Check for room booking conflicts
                    if (classes[i].get_meetingTime().get_id() == classes[j].get_meetingTime().get_id() or
                        classes[i].get_meetingTime().get_id() in classes[j].get_meetingTime().get_roomConflictingTimes()):
                        if classes[i].get_room() is not None and classes[j].get_room() is not None and \
                           classes[i].get_room().get_id() == classes[j].get_room().get_id():
                            roomBookingConflict = [classes[i], classes[j]]
                            self._conflicts.append(RoomBookingConflict(roomBookingConflict, classes[j].get_room()))
                            self._numOfConflicts += 1
    
                    # Check for class group booking conflicts
                    if (classes[i].get_meetingTime().get_id() == classes[j].get_meetingTime().get_id() or
                        classes[i].get_meetingTime().get_id() in classes[j].get_meetingTime().get_conflictingTimes()):
                        if classes[i].get_classGroup() == classes[j].get_classGroup():
                            classGroupBookingConflict = [classes[i], classes[j]]
                            self._conflicts.append(ClassGroupBookingConflict(classGroupBookingConflict, classes[j].get_classGroup()))
                            self._numOfConflicts += 1
    
        return 1 / (len(self._conflicts) + 1)
    
    def get_conflicts(self): return self._conflicts
    def __str__(self):
        returnValue = ""
        for i in range(0, len(self._classes)-1):
            returnValue += str(self._classes[i]) + ", "
        returnValue += str(self._classes[len(self._classes)-1])
        return returnValue

class Population:
    def __init__(self, size, data):
        self._size = size
        self._schedules = []
        for _ in range(0, size): self._schedules.append(Schedule(data).initialize())
    def get_schedules(self): return self._schedules

class GeneticAlgorithm:
    POPULATION_SIZE = 10
    NUMB_OF_ELITE_SCHEDULES = 1
    TOURNAMENT_SELECTION_SIZE = 3
    MUTATION_RATE = 0.01
    MAX_GENERATIONS = 5000
    def __init__(self, population_size=POPULATION_SIZE, max_generations=MAX_GENERATIONS):
        self.POPULATION_SIZE = population_size
        self.MAX_GENERATIONS = max_generations

    def evolve(self, population): return self._mutate_population(self._crossover_population(population))
    def _crossover_population(self, pop):
        data = pop.get_schedules()[0]._data
        crossover_pop = Population(0, data)
        for i in range(GeneticAlgorithm.NUMB_OF_ELITE_SCHEDULES):
            crossover_pop.get_schedules().append(pop.get_schedules()[i])
        i = GeneticAlgorithm.NUMB_OF_ELITE_SCHEDULES
        while i < GeneticAlgorithm.POPULATION_SIZE:
            schedule1 = self._select_tournament_population(pop).get_schedules()[0]
            schedule2 = self._select_tournament_population(pop).get_schedules()[0]
            crossover_pop.get_schedules().append(self._crossover_schedule(schedule1, schedule2))
            i += 1
        return crossover_pop
    def _mutate_population(self, population):
        for i in range(GeneticAlgorithm.NUMB_OF_ELITE_SCHEDULES, GeneticAlgorithm.POPULATION_SIZE):
            self._mutate_schedule(population.get_schedules()[i])
        return population
    def _crossover_schedule(self, schedule1, schedule2):
        data = schedule1._data
        crossoverSchedule = Schedule(data).initialize()
        for i in range(0, len(crossoverSchedule.get_classes())):
            if (rnd.random() > 0.5): crossoverSchedule.get_classes()[i] = schedule1.get_classes()[i]
            else: crossoverSchedule.get_classes()[i] = schedule2.get_classes()[i]
        return crossoverSchedule
    def _mutate_schedule(self, mutateSchedule):
        data = mutateSchedule._data
        schedule = Schedule(data).initialize()
        for i in range(0, len(mutateSchedule.get_classes())):
            if(GeneticAlgorithm.MUTATION_RATE > rnd.random()): mutateSchedule.get_classes()[i] = schedule.get_classes()[i]
        return mutateSchedule
    def _select_tournament_population(self, pop):
        data = pop.get_schedules()[0]._data
        tournament_pop = Population(0, data)
        i = 0
        while i < GeneticAlgorithm.TOURNAMENT_SELECTION_SIZE:
            tournament_pop.get_schedules().append(pop.get_schedules()[rnd.randrange(0, GeneticAlgorithm.POPULATION_SIZE)])
            i += 1
        tournament_pop.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        return tournament_pop

























    def format_remaining_time(self, remaining_time):
        td = timedelta(seconds=remaining_time)
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = ""
        if days > 0:
            time_str += f"{days} day{'s' if days > 1 else ''}"
        if hours > 0:
            if time_str:
                time_str += " and "
            time_str += f"{hours} hour{'s' if hours > 1 else ''}"
        if minutes > 0:
            if time_str:
                time_str += " and "
            time_str += f"{minutes} minute{'s' if minutes > 1 else ''}"
        if seconds > 0 and not time_str:
            time_str += f"{seconds} second{'s' if seconds > 1 else ''}"
        return time_str






    

    
    def run(self, data, user_info_list, initial_scheduler_data_ids):
        start_time = time.time()
        generationNumber = 0
        no_improvement_counter = 0
        previous_num_of_conflicts = None
    
        print("\n Generation # " + str(generationNumber))
        population = Population(self.POPULATION_SIZE, data)
        population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        DisplayManager().print_schedule_as_table(population.get_schedules()[0])
        scheduler_data_list = [InitialSchedulerData.objects.get(scheduler_id=data_id) for data_id in initial_scheduler_data_ids]
        
        with tqdm(total=self.MAX_GENERATIONS, desc="Progress", unit="generation") as pbar:
            while population.get_schedules()[0].get_fitness() != 1.0 and generationNumber < self.MAX_GENERATIONS:
                generationNumber += 1
                print("\n\nGeneration # " + str(generationNumber))
                population = self.evolve(population)
                population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
                DisplayManager().print_generation(population, generationNumber)
                # DisplayManager().print_schedule_as_table(population.get_schedules()[0])
                current_num_of_conflicts = population.get_schedules()[0].get_numOfConflicts()
                if previous_num_of_conflicts is not None and current_num_of_conflicts == previous_num_of_conflicts:
                    no_improvement_counter += 1
                else:
                    no_improvement_counter = 0
                previous_num_of_conflicts = current_num_of_conflicts
    
                if no_improvement_counter >= 100:
                    print("Terminating due to no improvement in number of conflicts for 100 generations.")
                    break
    
                progress_percentage = (generationNumber / self.MAX_GENERATIONS) * 100
                elapsed_time = time.time() - start_time
                estimated_total_time = elapsed_time / (generationNumber / self.MAX_GENERATIONS) 
                remaining_time = estimated_total_time - elapsed_time
    
                remaining_time_str = self.format_remaining_time(remaining_time)
                for scheduler_data in scheduler_data_list:
                    scheduler_data.progress = int(progress_percentage)
                    scheduler_data.remaining_time = remaining_time_str
                    scheduler_data.save()
                pbar.update(1)
                pbar.set_postfix(fitness=population.get_schedules()[0].get_fitness(), remaining_time=remaining_time_str)
    
        best_schedule = population.get_schedules()[0]
    
        end_time = time.time()
        total_generation_duration = end_time - start_time
        formatted_duration = self.format_remaining_time(total_generation_duration)
        result_identification = ResultIdentification.objects.create()
        with transaction.atomic():
            self.save_results(data, best_schedule, result_identification)
            generated_schedule = GeneratedSchedule(
                result_identification=result_identification,
                number_of_conflicts=best_schedule.get_numOfConflicts(),
                academic_year=InitialSchedulerData.objects.get(scheduler_id=initial_scheduler_data_ids[0]).academic_year,
                semester=InitialSchedulerData.objects.get(scheduler_id=initial_scheduler_data_ids[0]).semester,
                total_generation_duration=formatted_duration,
                population_size=self.POPULATION_SIZE,
                mutation_rate=self.MUTATION_RATE,
                number_of_elite_schedule=self.NUMB_OF_ELITE_SCHEDULES,
                number_of_generation=generationNumber,
                tournament_size=self.TOURNAMENT_SELECTION_SIZE
            )
            generated_schedule.save()
    
            # Add users to the generated schedule and collect institutes and programs
            institutes = set()
            programs = set()
            for user_id in user_info_list:
                user = User.objects.get(id=user_id)
                generated_schedule.created_by.add(user)
                if user.institute:
                    institutes.add(user.institute)
                if user.program:
                    programs.add(user.program)
    
            # Add institutes and programs to the generated schedule
            for institute in institutes:
                generated_schedule.institute = institute
                break
    
            for program in programs:
                generated_schedule.program.add(program)
    
            # Add initial scheduler data to the generated schedule
            for data_id in initial_scheduler_data_ids:
                initial_data = InitialSchedulerData.objects.get(scheduler_id=data_id)
                initial_data.generate_schedule = generated_schedule
                initial_data.result_identification = result_identification
                initial_data.save()
                generated_schedule.initial_scheduler_data.add(initial_data)
    
            generated_schedule.save()

    def save_results(self, data, results, result_identification):
        # Save Instructors
        for instructor in data['instructors']:
            instructor_id = int(instructor.get_id().lstrip('I').lstrip('0'))
            instructor_name = instructor.get_name()
            courses_data = instructor.get_courses()
            courses = []
            for course in courses_data:
                result_course, created = ResultCourse.objects.get_or_create(
                    course_id=course['course_id'],
                    result_identification=result_identification,
                )
                courses.append(result_course)
            result_instructor, created = ResultInstructor.objects.get_or_create(
                result_identification=result_identification,
                instructor_id=instructor_id,
                defaults={'instructor_name': instructor_name}
            )
            if not created:
                result_instructor.instructor_name = instructor_name
                result_instructor.save()
            result_instructor.courses.set(courses)
            result_instructor.save()
        
        # Save Classrooms
        for classroom in data['classrooms']:
            room_id = int(classroom.get_id().lstrip('R').lstrip('0'))
            room_name = classroom.get_roomName()
            is_lab = classroom.get_is_lab()
            result_classroom, created = ResultClassroom.objects.get_or_create(
                result_identification=result_identification,
                room_id=room_id,
                defaults={'room_name': room_name, 'is_lab': is_lab}
            )
            if not created:
                result_classroom.room_name = room_name
                result_classroom.is_lab = is_lab
                result_classroom.save()
    
        # Save Courses
        for course in data['courses']:
            course_id = int(course.get_id().lstrip('C').lstrip('0'))
            course_code = course.get_course_code()
            course_description = course.get_course_description()
            lecture_hours = course.get_lecture_hours()
            laboratory_hours = course.get_laboratory_hours()
            credit_units = course.get_creditHour()
            year_level = course.get_year_level()
            program = course.get_program()
            result_course, created = ResultCourse.objects.get_or_create(
                course_id=course_id,
                result_identification=result_identification,
                defaults={
                    'course_code': course_code,
                    'course_description': course_description,
                    'lecture_hours': lecture_hours,
                    'laboratory_hours': laboratory_hours,
                    'credit_units': credit_units,
                    'year_level': year_level,
                    'program_id': program
                }
            )
            if not created:
                result_course.course_code = course_code
                result_course.course_description = course_description
                result_course.lecture_hours = lecture_hours
                result_course.laboratory_hours = laboratory_hours
                result_course.credit_units = credit_units
                result_course.year_level = year_level
                result_course.program_id = program
                result_course.save()
    
        # Save Class Groups
        for class_group in data['class_groups']:
            year_level = class_group.get_year_level()
            class_group_id = int(class_group.get_id().lstrip('G').lstrip('0')) if class_group.get_id().lstrip('G').lstrip('0') else 0
            class_group_name = class_group.get_name()
            schedule_courses_data = class_group.get_scheduleCourses()
            schedule_courses = []
            for course in schedule_courses_data:
                result_course, created = ResultCourse.objects.get_or_create(course_id=int(course.get_id().lstrip('C').lstrip('0')), result_identification=result_identification)
                schedule_courses.append(result_course)
            result_class_group = ResultClassGroup.objects.create(
                result_identification=result_identification,
                class_group_id=class_group_id,
                class_group_name=class_group_name,
                year_level=year_level
            )
            result_class_group.schedule_courses.set(schedule_courses)
            result_class_group.save()

              # Save Meeting Times
              # Save Meeting Times
              
        meeting_id_mapping = {}

        # Save Meeting Times
        for meeting_time in data['meeting_times']:
            old_meeting_id = int(meeting_time.get_id().lstrip('M').lstrip('0'))
            meeting_time_value = meeting_time.get_time()
            
            # Get schedule details
            schedule_details = get_schedule_details(meeting_time_value)
            if schedule_details:
                days = split_days(schedule_details)
                time_range = schedule_details.get('Time', '')
                if time_range:
                    start_time, end_time = time_range.split(' - ')
                else:
                    start_time = ''
                    end_time = ''
            else:
                days = []
                start_time = ''
                end_time = ''
            
            new_meeting_ids = []
            for day in days:
                is_online_meeting = day.strip() in schedule_details.get('Online', '').split(',') if schedule_details and schedule_details.get('Online') else False
                
                # Create a new meeting_id for each day
                result_meeting_time = ResultMeetingTime.objects.create(
                    result_identification=result_identification,
                    meeting_day=day.strip(),
                    start_time=start_time,
                    end_time=end_time,
                    is_online_meeting=is_online_meeting
                )
                
                # Set the meeting_id to be the same as result_id
                result_meeting_time.meeting_id = result_meeting_time.result_id
                result_meeting_time.save()
                
                new_meeting_ids.append(result_meeting_time.meeting_id)  # Store the new meeting_id
            
            # Store the mapping of old meeting ID to new meeting IDs
            meeting_id_mapping[old_meeting_id] = new_meeting_ids


        # Save Programs
        for program in data['programs']:
            program_id = program.get_id()
            program_name = program.get_name()
            program_code = program.get_program_code()
            result_program, created = ResultProgram.objects.get_or_create(
                result_identification=result_identification,
                program_id=program_id,
                defaults={
                    'program_name': program_name,
                    'program_code': program_code
                }
            )
            if not created:
                result_program.program_name = program_name
                result_program.program_code = program_code
                result_program.save()


    # Save Timetable
        if results:
            for class_obj in results.get_classes():
                instructor = class_obj.get_instructor()
                class_group = class_obj.get_classGroup()
                course = class_obj.get_course()
                classroom = class_obj.get_room()
                meeting_time = class_obj.get_meetingTime()
                instructor_id = int(instructor.get_id().lstrip('I').lstrip('0')) if instructor else None
                class_group_id = int(class_group.get_id().lstrip('G').lstrip('0')) if class_group else None
                course_id = int(course.get_id().lstrip('C').lstrip('0')) if course else None
                classroom_id = int(classroom.get_id().lstrip('R').lstrip('0')) if classroom else None
                old_meeting_id = int(meeting_time.get_id().lstrip('M').lstrip('0')) if meeting_time else None
                
                # Create ResultTimetable entry
                result_timetable = ResultTimetable.objects.create(
                    result_identification=result_identification,
                    instructor_id=instructor_id,
                    class_group_id=class_group_id,
                    course_id=course_id
                )
                
                # Create ResultTimetableDetail entries for each new meeting ID
                if old_meeting_id in meeting_id_mapping:
                    for new_meeting_id in meeting_id_mapping[old_meeting_id]:
                        ResultTimetableDetail.objects.create(
                            result_identification=result_identification,
                            room_id=classroom_id,
                            meeting_id=new_meeting_id,
                            result_timetable=result_timetable
                        )
                
                result_timetable.save()

class DisplayManager:
    def print_generation(self, population, generationNumber):
        print("\nGeneration # " + str(generationNumber))
        for i, schedule in enumerate(population.get_schedules()):
            print(f"Schedule {i + 1}: Fitness = {schedule.get_fitness()} | Number of Conflicts = {schedule.get_numOfConflicts()}")

    def print_schedule_as_table(self, schedule):
        classes = schedule.get_classes()
        scheduleTable = PrettyTable(["Id", "Class Group", "Course Code", "Room", "Meeting (Time & Day)", "Instructor"])
        for i in range(0, len(classes)):
            class_group_name = classes[i]._classGroup.get_name() if classes[i]._classGroup else "N/A"
            course_code = classes[i]._course.get_course_code() if classes[i]._course else "N/A"
            room_name = classes[i]._room.get_roomName() if classes[i]._room else "N/A"
            meeting_time = classes[i]._meetingTime.get_time() if classes[i]._meetingTime else "N/A"
            instructor_name = classes[i]._instructor.get_name() if classes[i]._instructor else "N/A"
            scheduleTable.add_row([str(i), class_group_name, course_code, room_name, meeting_time, instructor_name])
        print(scheduleTable)