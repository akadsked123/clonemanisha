from django.db import models
from apps.curriculum.models import Programs
from apps.institutes.models import Institutes
from apps.user.models import User

class Periods(models.Model):
    period_id = models.AutoField(primary_key=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
    
    class Meta:
        db_table = "Periods"
        verbose_name = 'Period'
        verbose_name_plural = 'Periods'
        indexes = [
            models.Index(fields=['period_id']),
        ]

class Weekday(models.Model):
    day_id = models.AutoField(primary_key=True)
    day_name = models.CharField(max_length=9, unique=True)
    
    def __str__(self):
        return self.day_name
    
    class Meta:
        db_table = "Weekday"
        verbose_name = 'Weekday'
        verbose_name_plural = 'Weekdays'

class InitialSchedulerData(models.Model):
    STATUS_CHOICES = (
      (1, 'Inactive'),
      (2, 'Pending'),
      (3, 'Processing'),
      (4, 'Completed'),
      (5, 'Error'),
      (6, 'Cancelled'),
    )
    scheduler_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=100, null=True, blank=True)
    semester = models.CharField(max_length=100, null=True, blank=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institutes, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)
    remaining_time = models.CharField(max_length=50, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=2)
    initial_data_json_file = models.FileField(upload_to='scheduler_data/', null=True, blank=True)
    generate_schedule = models.ForeignKey('GeneratedSchedule', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
          db_table = "initial_scheduler_data"
          verbose_name = 'Initial Scheduler Data'
          verbose_name_plural = 'Initial Scheduler Data'
          constraints = [
              models.UniqueConstraint(
                  fields=['institute', 'program', 'semester'],
                  condition=models.Q(status__in=[2, 3]),
                  name='unique_active_processing_per_institute_program_semester'
              )
          ]
          indexes = [
              models.Index(fields=['result_identification']),
              models.Index(fields=['scheduler_id']),
          ]

class ResultIdentification(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "result_identification"
        verbose_name = 'Result Identification'
        verbose_name_plural = 'Result Identifications'
        indexes = [
            models.Index(fields=['result_id']),
        ]

class GeneratedSchedule(models.Model):
    id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    number_of_conflicts = models.IntegerField(default=0, null=True, blank=True)
    academic_year = models.CharField(max_length=100, null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    institute = models.ForeignKey(Institutes, on_delete=models.CASCADE, null=True, blank=True)
    program = models.ManyToManyField(Programs, blank=True)
    created_by = models.ManyToManyField(User)
    total_generation_duration = models.CharField(max_length=50, null=True, blank=True)
    initial_scheduler_data = models.ManyToManyField(InitialSchedulerData, blank=True)
    population_size = models.IntegerField(null=True, blank=True)
    mutation_rate = models.FloatField(null=True, blank=True)
    number_of_elite_schedule = models.IntegerField(null=True, blank=True)
    number_of_generation = models.IntegerField(null=True, blank=True)
    tournament_size = models.IntegerField(null=True, blank=True)
    

    class Meta:
        db_table = "generated_schedule"
        verbose_name = 'Generated Schedule'
        verbose_name_plural = 'Generated Schedules'
        constraints = [
            models.UniqueConstraint(fields=['result_identification'], name='unique_result_identification')
        ]
        indexes = [
            models.Index(fields=['result_identification']),
        ]

class ViewTimetable(models.Model):
    id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    share_to_instructor = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "view_timetable"
        verbose_name = 'View Timetable'
        verbose_name_plural = 'View Timetables'
        unique_together = ('user', 'result_identification')
        indexes = [
                models.Index(fields=['result_identification']),
            ]

class ResultInstructor(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    instructor_name = models.CharField(max_length=255, null=True, blank=True)
    courses = models.ManyToManyField('ResultCourse', related_name='instructors', blank=True)
    availability = models.ManyToManyField('ResultMeetingTime', related_name='available_instructors',  blank=True)

    class Meta:
        db_table = "result_instructor"
        verbose_name = 'Result Instructor'
        verbose_name_plural = 'Result Instructors'
        indexes = [
                models.Index(fields=['result_identification']),
            ]

class ResultClassroom(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    room_id = models.IntegerField(null=True, blank=True)
    room_name = models.CharField(max_length=255, null=True, blank=True)
    is_lab = models.BooleanField(default=False)
        
    class Meta:
        db_table = "result_classroom"
        verbose_name = 'Result Classroom'
        verbose_name_plural = 'Result Classrooms'
        indexes = [
            models.Index(fields=['result_identification']),
        ]

class ResultProgram(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    program_id = models.IntegerField(null=True, blank=True)
    program_name = models.CharField(max_length=255, null=True, blank=True)
    program_code = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "result_program"
        verbose_name = 'Result Program'
        verbose_name_plural = 'Result Programs'
        indexes = [
                models.Index(fields=['result_identification']),
            ]

class ResultClassGroup(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    class_group_id = models.IntegerField(null=True, blank=True)
    class_group_name = models.CharField(max_length=255, null=True, blank=True)
    schedule_courses = models.ManyToManyField('ResultCourse', related_name='class_groups', blank=True)
    year_level = models.IntegerField()

    class Meta:
        db_table = "result_class_group"
        verbose_name = 'Result Class Group'
        verbose_name_plural = 'Result Class Groups'
        indexes = [
                models.Index(fields=['result_identification']),
            ]
        unique_together = ('result_identification', 'class_group_id')
        
class ResultMeetingTime(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    meeting_id = models.IntegerField(null=True, blank=True)
    meeting_day = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.CharField(max_length=255, null=True, blank=True)
    end_time = models.CharField(max_length=255, null=True, blank=True)
    is_online_meeting = models.BooleanField(default=False)

    class Meta:
            db_table = "result_meeting_time"
            verbose_name = 'Result Meeting Time'
            verbose_name_plural = 'Result Meeting Times'
            indexes = [
                models.Index(fields=['result_identification']),
            ]
            
class ResultCourse(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    course_id = models.IntegerField()
    course_code = models.CharField(max_length=255)
    course_description = models.TextField(max_length=255)
    lecture_hours = models.IntegerField(null=True, blank=True)
    laboratory_hours = models.IntegerField(null=True, blank=True)
    credit_units = models.IntegerField(null=True, blank=True)
    year_level = models.IntegerField(null=True, blank=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'result_course'
        verbose_name = 'Result Course'
        verbose_name_plural = 'Result Courses'
        indexes = [
            models.Index(fields=['result_identification']),
        ]

class ResultTimetableDetail(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    room_id = models.IntegerField(null=True, blank=True)
    meeting_id = models.IntegerField(null=True, blank=True)
    result_timetable = models.ForeignKey('ResultTimetable', on_delete=models.CASCADE, related_name='details')

    class Meta:
        db_table = 'result_timetable_detail'
        verbose_name = 'Result Timetable Detail'
        verbose_name_plural = 'Result Timetable Details'
        indexes = [
            models.Index(fields=['result_identification']),
        ]
        unique_together = ('result_id', 'result_identification', 'room_id', 'meeting_id')

class ResultTimetable(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    class_group_id = models.IntegerField(null=True, blank=True)
    course_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'result_timetable'
        verbose_name = 'Result Timetable'
        verbose_name_plural = 'Result Timetables'
        indexes = [
            models.Index(fields=['result_identification']),
        ]
        unique_together = ('result_id', 'result_identification', 'instructor', 'class_group_id', 'course_id')

class InitialCourseAssignment(models.Model):
    assignment_id = models.BigAutoField(primary_key=True)
    result_identification = models.ForeignKey('ResultIdentification', on_delete=models.CASCADE, null=True, blank=True)
    course_id = models.ForeignKey('ResultCourse', on_delete=models.CASCADE, null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_assign = models.BooleanField(default=False, null=True, blank=True)
    
    class Meta:
        db_table = 'initial_course_assignment'
        verbose_name = 'Initial Course Assignment'
        verbose_name_plural = 'Initial Course Assignments'
        indexes = [
            models.Index(fields=['result_identification']),
        ]