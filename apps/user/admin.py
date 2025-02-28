from django.contrib import admin
from apps.user.models import AdminLoadRelease, FacultyProfile, GroupMember, Notification, REPLoadRelease, User, UserGroup

class ListOfUsers(admin.ModelAdmin):
    list_display = ('username', 'first_name','middle_name','last_name','suffix', 'gender','email', 'user_type','employment_status','institute_name', 'program_name', 'position','is_active','last_login','date_joined',)
    list_display_links = ('username','first_name','middle_name','last_name','suffix', 'gender','email', 'user_type','employment_status', 'institute_name', 'program_name', 'position','is_active','last_login','date_joined',)

    def program_name(self, obj):
        return obj.program.program_name if obj.program else 'REQIURED FIELD'
    
    def institute_name(self, obj):
        return obj.institute.institute_name if obj.institute else 'REQIURED FIELD'
    
admin.site.register(User, ListOfUsers)

class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'group_name', 'semester', 'program', 'institute', 'curriculum', 'date_created','date_updated', )
    list_display_links =  ('group_id', 'group_name', 'semester', 'program', 'institute', 'curriculum', 'date_created','date_updated', )
    search_fields = ('group_name',)
    readonly_fields = ('date_created',)

admin.site.register(UserGroup, UserGroupAdmin)

class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'group', 'user', 'program', 'institute', 'display_courses', 'date_assigned', 'date_added')
    list_display_links = ('member_id', 'group', 'user')
    search_fields = ('user__first_name', 'user__last_name', 'group__group_name')
    list_filter = ('group', 'program', 'institute')
    readonly_fields = ('date_assigned', 'date_added')

    def display_courses(self, obj):
        return ", ".join([course.course_code for course in obj.courses.all()])
    display_courses.short_description = 'Courses'

admin.site.register(GroupMember, GroupMemberAdmin)

class notificationAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'message', 'status', 'date_time', 'created_at', 'recipient', 'sender')
    list_display_links = ('notification_id', 'message', 'status', 'date_time', 'created_at', 'recipient', 'sender')
    search_fields = ('message',)
    list_filter = ('status', 'date_time', 'created_at')
    readonly_fields = ('created_at',)

admin.site.register(Notification, notificationAdmin)


class UndergraduateDegreeInline(admin.TabularInline):
    model = FacultyProfile.undergraduate_degrees.through
    extra = 1

class GraduateDegreeInline(admin.TabularInline):
    model = FacultyProfile.graduate_degrees.through
    extra = 1

class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'user', 'academic_rank', 'display_undergraduate_degrees', 'display_graduate_degrees', 'employment_status', 'institute', 'program', 'designation', 'department', 'core_time', 'student_consultation_time', 'date_hired', 'date_created', 'date_updated')
    list_display_links = ('faculty_id', 'user', 'academic_rank', 'display_undergraduate_degrees', 'display_graduate_degrees', 'employment_status', 'institute', 'program', 'designation', 'department', 'core_time', 'student_consultation_time', 'date_hired', 'date_created', 'date_updated')
    search_fields = ('user__username', 'academic_rank', 'undergraduate_degrees__name', 'graduate_degrees__name', 'employment_status', 'institute__institute_name', 'program__program_name', 'designation', 'department')
    list_filter = ('employment_status', 'institute', 'program', 'date_hired', 'date_created')
    readonly_fields = ('date_created', 'date_updated')
    inlines = [UndergraduateDegreeInline, GraduateDegreeInline]

    def display_undergraduate_degrees(self, obj):
        return ", ".join([degree.name for degree in obj.undergraduate_degrees.all()])
    display_undergraduate_degrees.short_description = 'Undergraduate Degrees'

    def display_graduate_degrees(self, obj):
        return ", ".join([degree.name for degree in obj.graduate_degrees.all()])
    display_graduate_degrees.short_description = 'Graduate Degrees'

admin.site.register(FacultyProfile, FacultyProfileAdmin)

class AdminLoadReleaseAdmin(admin.ModelAdmin):
    list_display = ('description', 'user', 'hour', 'unit', 'date_created', 'date_updated')
    search_fields = ('description', 'user__username')
    list_filter = ('date_created', 'date_updated')
    readonly_fields = ('date_created', 'date_updated')

admin.site.register(AdminLoadRelease, AdminLoadReleaseAdmin)

class REPLoadReleaseAdmin(admin.ModelAdmin):
    list_display = ('description', 'user', 'hour', 'unit', 'date_created', 'date_updated')
    search_fields = ('description', 'user__username')
    list_filter = ('date_created', 'date_updated')
    readonly_fields = ('date_created', 'date_updated')

admin.site.register(REPLoadRelease, REPLoadReleaseAdmin)