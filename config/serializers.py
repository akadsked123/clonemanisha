from rest_framework import serializers
from apps.curriculum.models import Courses
from apps.timetable.models import InitialSchedulerData, ResultClassGroup, ResultClassroom, ResultCourse, ResultInstructor, ResultMeetingTime, ResultTimetable
from apps.user.models import AdminLoadRelease, GroupMember, Notification, REPLoadRelease, User

class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = ['course_id', 'course_code', 'course_description']
        
class GroupMemberSerializer(serializers.ModelSerializer):
    courses = CoursesSerializer(many=True, read_only=True)

    class Meta:
        model = GroupMember
        fields = ['user', 'courses']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'profile_image']

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    class Meta:
        model = Notification
        fields = '__all__'

class InitialSchedulerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialSchedulerData
        fields = ['scheduler_id', 'progress', 'remaining_time', 'status']

# =======================================================================================================
# The following serializers are for data generated from a genetic algorithm.
# These serializers will be used for final customization of the scheduling data.
# =======================================================================================================

# Meeting Times API
class ResultMeetingTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultMeetingTime
        fields = ['result_id', 'meeting_time', 'credit_hours']

# Courses API
class ResultCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultCourse
        fields = ['course_id', 'course_code', 'course_description', 'lecture_hours', 'laboratory_hours', 'credit_units']

# Instructors API
class ResultCourseIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultCourse
        fields = ['course_id']

class ResultMeetingTimeIdSerializer(serializers.ModelSerializer):
    conflicts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
            model = ResultMeetingTime
            fields = ['result_id', 'meeting_time', 'credit_hours', 'conflicts']

class ResultInstructorSerializer(serializers.ModelSerializer):
    courses = ResultCourseIdSerializer(many=True)
    availability = ResultMeetingTimeIdSerializer(many=True)
    program_code = serializers.CharField(source='instructor.program.program_code', read_only=True)

    class Meta:
        model = ResultInstructor
        fields = ['instructor_id', 'instructor_name', 'courses', 'availability', 'program_code']
        
# Timetable API
class ResultTimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultTimetable
        fields = ['instructor_id', 'class_group_id', 'course_id', 'classroom_id', 'meeting_time_id']

# Classrooms API
class ResultClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultClassroom
        fields = ['room_id', 'room_name', 'is_lab']

# Year Levels API
class ResultClassGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultClassGroup
        fields = ['class_group_id', 'class_group_name']

# =======================================================================================================
# End of Data Generated from Genetic Algorithm Serializers
# =======================================================================================================

class AdminLoadReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminLoadRelease
        fields = '__all__'

class REPLoadReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = REPLoadRelease
        fields = '__all__'