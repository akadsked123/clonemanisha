from django import forms
from django.contrib import admin
from apps.curriculum.models import Rooms, Courses,  CurriculumYear, Programs

class RoomsAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'room_name', 'is_lab' ,'building', 'date_added')
    list_display_links = ('room_id', 'room_name', 'is_lab','building', 'date_added')
    list_filter = ('is_lab',)
    search_fields = ('room_name',)
admin.site.register(Rooms, RoomsAdmin)

class ProgramsAdmin(admin.ModelAdmin):
    list_display = ('program_id', 'program_code', 'program_name', 'program_slug')
    list_display_links = ('program_id', 'program_code', 'program_name', 'program_slug')
    search_fields = ('program_code', 'program_name')
admin.site.register(Programs, ProgramsAdmin)

class CurriculumYearAdmin(admin.ModelAdmin):
    list_display = ('curriculum_id', 'curriculum_year', 'institute', 'program')
    list_display_links =  ('curriculum_id', 'curriculum_year', 'institute', 'program')
    search_fields =  ('curriculum_id', 'curriculum_year')

    def institute(self, obj):
        return obj.institute.institute_name if obj.institute else 'N/A'
    
    def program(self, obj):
        return obj.program.program_name if obj.program else 'N/A'
    
admin.site.register(CurriculumYear, CurriculumYearAdmin)

# Search Filter
class ProgramCodeFilter(admin.SimpleListFilter):
    title = 'Program Code'
    parameter_name = 'program_code'

    def lookups(self, request, model_admin):
        # Look up distinct program_code values from the Programs model
        return Programs.objects.values_list('program_code', 'program_code').distinct()

    def queryset(self, request, queryset):
        if self.value():
            # Filter Courses based on the program_code from the related Programs model
            return queryset.filter(program__program_code=self.value())
        return queryset


class CoursesAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'curriculum_year', 'program_code', 'program_name', 'year_level', 'course_code', 'course_description', 'lecture', 'laboratory', 'credit_units', 'semester', 'created_at', 'updated_at', 'is_lab')
    list_display_links = ('course_id','curriculum_year', 'program_code', 'program_name', 'year_level', 'course_code', 'course_description', 'lecture', 'laboratory', 'credit_units', 'semester', 'created_at', 'updated_at', 'is_lab')
    search_fields = ('course_code', 'program_code')
    exclude = ('credit_units', 'is_lab')
    list_filter = (ProgramCodeFilter,)

    def program_code(self, obj):
        return obj.program.program_code if obj.program else 'N/A'

    def program_name(self, obj):
        return obj.program.program_name if obj.program else 'N/A'

    def curriculum_year(self, obj):
        return obj.curriculum.curriculum_year if obj.curriculum else 'N/A'


admin.site.register(Courses, CoursesAdmin)




