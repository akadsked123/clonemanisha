from django.contrib import admin
from apps.timetable.models import (
    GeneratedSchedule, InitialCourseAssignment, InitialSchedulerData, Periods, 
    ResultClassGroup, ResultClassroom, ResultCourse, ResultIdentification, 
    ResultInstructor, ResultMeetingTime, ResultProgram, ResultTimetable, 
    ViewTimetable, Weekday
)

class PeriodsAdmin(admin.ModelAdmin):
    list_display = ('period_id', 'start_time', 'end_time', 'created_at', 'updated_at')
    search_fields = ('start_time', 'end_time')

class WeekdayAdmin(admin.ModelAdmin):
    list_display = ('day_id', 'day_name')
    search_fields = ('day_name',)

class InitialSchedulerDataAdmin(admin.ModelAdmin):
    list_display = ('scheduler_id', 'created_by', 'academic_year', 'semester', 'program', 'institute', 'created_at', 'progress', 'remaining_time', 'status')
    search_fields = ('academic_year', 'semester', 'program__program_name', 'institute__name', 'status')
    list_filter = ('status', 'created_at')

class ResultIdentificationAdmin(admin.ModelAdmin):
    list_display = ('result_id', 'created_at')
    search_fields = ('result_id',)

class GeneratedScheduleAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'number_of_conflicts', 'total_generation_duration', 'population_size', 'mutation_rate', 'number_of_elite_schedule', 'number_of_generation', 'tournament_size')
    search_fields = ('academic_year', 'semester', 'institute__name')
    list_filter = ('created_at',)

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

class ViewTimetableAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'share_to_instructor', 'user')
    search_fields = ('result_identification__result_id', 'user__username')
    list_filter = ('share_to_instructor',)

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

class ResultInstructorAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'instructor_id', 'instructor_name')
    search_fields = ('instructor_name',)

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

class ResultClassroomAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'room_id', 'room_name', 'is_lab')
    search_fields = ('room_name',)
    list_filter = ('is_lab',)

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

class ResultProgramAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'program_id', 'program_name', 'program_code')
    search_fields = ('program_name', 'program_code')

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

class ResultClassGroupAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'class_group_id', 'class_group_name', 'year_level')
    search_fields = ('class_group_name',)
    list_filter = ('year_level',)

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

class ResultMeetingTimeAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'meeting_id', 'meeting_day', 'start_time', 'end_time', 'is_online_meeting')
    search_fields = ('meeting_day', 'start_time', 'end_time')

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

class ResultCourseAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'course_id', 'course_code', 'course_description', 'lecture_hours', 'laboratory_hours', 'credit_units')
    search_fields = ('course_code', 'course_description')

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

class ResultTimetableAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'instructor_id', 'class_group_id', 'course_id')
    search_fields = ('instructor_id', 'class_group_id', 'course_id')

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

class InitialCourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_result_identification', 'get_course_code', 'instructor_id', 'is_assign')
    search_fields = ('result_identification__result_id', 'course_id__course_code', 'instructor_id__username')
    list_filter = ('is_assign',)

    def get_result_identification(self, obj):
        return obj.result_identification.result_id
    get_result_identification.short_description = 'Result Identification'

    def get_course_code(self, obj):
        return obj.course_id.course_code
    get_course_code.short_description = 'Course Code'

admin.site.register(InitialCourseAssignment, InitialCourseAssignmentAdmin)
admin.site.register(Periods, PeriodsAdmin)
admin.site.register(Weekday, WeekdayAdmin)
admin.site.register(ResultIdentification, ResultIdentificationAdmin)
admin.site.register(ResultInstructor, ResultInstructorAdmin)
admin.site.register(ResultClassroom, ResultClassroomAdmin)
admin.site.register(ResultProgram, ResultProgramAdmin)
admin.site.register(ResultClassGroup, ResultClassGroupAdmin)
admin.site.register(ResultMeetingTime, ResultMeetingTimeAdmin)
admin.site.register(ResultCourse, ResultCourseAdmin)
admin.site.register(ResultTimetable, ResultTimetableAdmin)
admin.site.register(InitialSchedulerData, InitialSchedulerDataAdmin)
admin.site.register(GeneratedSchedule, GeneratedScheduleAdmin)
admin.site.register(ViewTimetable, ViewTimetableAdmin)