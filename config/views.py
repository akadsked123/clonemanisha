import mimetypes
import os
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from apps.curriculum.models import Courses, Programs
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from apps.timetable.get_vacant_time_classroom import get_vacant_time_slots
from apps.timetable.models import  InitialSchedulerData, ResultClassGroup, ResultClassroom, ResultCourse, ResultIdentification, ResultInstructor, ResultMeetingTime, ResultTimetable
from apps.timetable.schedule_class_group import class_group_timetable
from apps.timetable.schedule_classroom import classroom_timetable
from apps.timetable.schedule_instructor import instructor_timetable
from apps.user.models import GroupMember, Notification, UserGroup
from config.serializers import CoursesSerializer, GroupMemberSerializer, InitialSchedulerDataSerializer, NotificationSerializer, ResultClassGroupSerializer, ResultClassroomSerializer, ResultCourseSerializer, ResultInstructorSerializer, ResultMeetingTimeIdSerializer, ResultTimetableSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from apps.user.models import AdminLoadRelease, REPLoadRelease
from config.serializers import AdminLoadReleaseSerializer, REPLoadReleaseSerializer

@login_required
def home_redirect(request):
    user = request.user
    if user.user_type == 5:
        return redirect('/timetable/my-schedule/')
    elif user.user_type == 1:
        return redirect('/curriculum/curriculum-maintenance-and-management/')
    else:
        recent_group_with_members = UserGroup.objects.order_by('-date_created').filter(
        groupmember__isnull=False,
        program=user.program,
        institute=user.institute
      ).first()
        if recent_group_with_members:
            return redirect(f'/dashboard?group={recent_group_with_members.group_id}&page=1&items_per_page=25')
        else:
            return redirect('/dashboard')

def hello_world_view(request):
    return HttpResponse("Hello World")

@login_required
@require_GET
@csrf_exempt
def check_unique(request):
    field = request.GET.get('field')
    value = request.GET.get('value')
    if field not in ['program_code', 'program_name']:
        return JsonResponse({'error': 'Invalid field'}, status=400)
    exists = Programs.objects.filter(**{field: value}).exists()
    return JsonResponse({'exists': exists})

@method_decorator(login_required(login_url='/accounts/login/'),  name='dispatch')
class CourseListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    def get(self, request, *args, **kwargs):
        try:
            # Get filter parameters from the request
            program_id = request.query_params.get('program_id')
            institute_id = request.query_params.get('institute_id')
            curriculum_id = request.query_params.get('curriculum_id')
            semester = request.query_params.get('semester')

            # Filter courses based on the provided parameters
            courses = Courses.objects.filter(
                program__program_id=program_id,
                program__institute_id=institute_id,
                curriculum__curriculum_id=curriculum_id,
                semester=semester
            )

            # Serialize the filtered courses
            serializer = CoursesSerializer(courses, many=True)

            # Return the serialized data in JSON format
            return JsonResponse(serializer.data, safe=False)

        except Courses.DoesNotExist:
            return JsonResponse({'error': 'No courses found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

class UserCoursesView(generics.RetrieveAPIView):
  serializer_class = GroupMemberSerializer
  authentication_classes = [SessionAuthentication, BasicAuthentication]
  permission_classes = [IsAuthenticated]

  def get_object(self):
    member_id = self.kwargs.get('member_id')
    try:
      return GroupMember.objects.get(pk=member_id)
    except GroupMember.DoesNotExist:
      raise Http404("GroupMember matching query does not exist.")

# ==================================== Prepare Scheduler Data ====================================
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class SchedulerDataAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated

    def get(self, request, user_group_id):
        # Get UserGroup by ID
        user_group = get_object_or_404(UserGroup, group_id=user_group_id)

        # Check permissions
        if request.user.user_type != 4:
            raise PermissionDenied("Access denied")
        if request.user.program != user_group.program:
            raise PermissionDenied("Access denied")
        if request.user.institute != user_group.institute:
            raise PermissionDenied("Access denied")

        # Get instructors with courses assigned to them for the selected UserGroup
        instructors_with_courses = GroupMember.objects.filter(group=user_group).prefetch_related('courses')

        # Get courses from the curriculum using the curriculum_id FK in UserGroup and filter by semester
        courses = Courses.objects.filter(
            curriculum=user_group.curriculum,
            semester=user_group.semester
        )

        # Prepare the JSON structure based on the specific UserGroup
        response_data = {
            'institute': {
                'institute_id': user_group.institute.institute_id,
                'institute_name': user_group.institute.institute_name,
                'programs': [
                    {
                        'program_id': user_group.program.program_id,
                        'program_code': user_group.program.program_code,
                        'program_name': user_group.program.program_name,
                        'semester': int(user_group.semester),
                        'curriculum_year': user_group.group_name,
                        'course_levels': [
                            {
                                'year_level': year_level,
                                'number_of_classes': 0,
                                'courses': [
                                    {
                                        'course_id': course.course_id,
                                        'course_code': course.course_code,
                                        'course_description': course.course_description,
                                        'lecture_hours': course.lecture,
                                        'laboratory_hours': course.laboratory,
                                        'credit_units': course.credit_units,
                                    } for course in courses if course.year_level == year_level
                                ]
                            }
                            for year_level in courses.values_list('year_level', flat=True).distinct()
                        ]
                    }
                ],
                'instructors': [
                    {
                        'instructor_id': instructor.user.id,
                        'instructor_name': instructor.user.get_full_name().title(),
                        'courses': [
                            {
                                'course_id': course.course_id,
                            } for course in instructor.courses.all()
                        ]
                    } for instructor in instructors_with_courses
                ]
            }
        }

        return Response(response_data)

# ==================================== Protected Media View ====================================
class ProtectedMediaView(View):
  def get(self, request, path):
    # Check if the path is a directory
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.isdir(file_path):
      raise Http404("Directory access is forbidden.")

    # Check if the file exists
    if os.path.exists(file_path):
      mime_type, _ = mimetypes.guess_type(file_path)
      mime_type = mime_type if mime_type else 'application/octet-stream'
      with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=mime_type)
        response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
        return response

    raise Http404("File does not exist.")
  
# ==================================== End for Protected Media View ====================================

# ==================================== Notification List View ====================================

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')[:10]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_unread = Notification.objects.filter(recipient=self.request.user, is_read=False).count()
        total_unread_display = '9+' if total_unread > 9 else total_unread
        return Response({
            'notifications': serializer.data,
            'total_unread': total_unread_display
        })
  
#===================================== Initial Data ====================================
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InitialSchedulerDataViewSet(viewsets.ModelViewSet):
    queryset = InitialSchedulerData.objects.all()
    serializer_class = InitialSchedulerDataSerializer

# ==================================== Timetable API Views ====================================
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class TimetableAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, result_identification, *args, **kwargs):
        timetables = ResultTimetable.objects.filter(result_identification=result_identification)
        if not timetables.exists():
            raise Http404("No timetables found.")
        serializer = ResultTimetableSerializer(timetables, many=True)
        return Response({'timetable': serializer.data})
    
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ClassroomsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, result_identification, *args, **kwargs):
        classrooms = ResultClassroom.objects.filter(result_identification=result_identification)
        if not classrooms.exists():
            raise Http404("No classrooms found.")
        serializer = ResultClassroomSerializer(classrooms, many=True)
        return Response({'classrooms': serializer.data})
        
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class MeetingTimesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, result_identification, *args, **kwargs):
        meeting_times = ResultMeetingTime.objects.filter(result_identification=result_identification)
        if not meeting_times.exists():
            raise Http404("No meeting times found.")
        serializer = ResultMeetingTimeIdSerializer(meeting_times, many=True)
        return Response({'meeting_times': serializer.data})

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InstructorsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, result_identification, *args, **kwargs):
        instructors = ResultInstructor.objects.filter(result_identification=result_identification).order_by('instructor_name')
        if not instructors.exists():
            raise Http404("No instructors found.")
        serializer = ResultInstructorSerializer(instructors, many=True)
        return Response({'instructors': serializer.data})
    
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class CoursesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, result_identification, *args, **kwargs):
        courses = ResultCourse.objects.filter(result_identification=result_identification)
        if not courses.exists():
            raise Http404("No courses found.")
        serializer = ResultCourseSerializer(courses, many=True)
        return Response({'courses': serializer.data})

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ClassGroupsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, result_identification, *args, **kwargs):
        class_groups = ResultClassGroup.objects.filter(result_identification=result_identification)
        if not class_groups.exists():
            raise Http404("No class groups found.")
        serializer = ResultClassGroupSerializer(class_groups, many=True)
        return Response({'class_groups': serializer.data})
# ==================================== End for Timetable API Views ====================================

# ==================================== Select Class Groups API View ====================================
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class FilteredClassGroupsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, result_identification, year_level, course_id, *args, **kwargs):
        print(f"Year Level: {year_level}, Course ID: {course_id}, Result ID: {result_identification}")
        # Get the course to determine the program code
        course = get_object_or_404(ResultCourse, result_identification=result_identification, result_id=course_id)
        print(f"Course ID: {course.course_id}, Course Name: {course.course_code}, Result ID: {result_identification}")
        # Example: Course ID: 49, Course Name: IT422, Result ID: 109
        program_code = course.program.program_code
    
        # Filter class groups based on the first four letters of the class group name and order them
        class_groups = ResultClassGroup.objects.filter(
            result_identification=result_identification,
            year_level=year_level,
            class_group_name__startswith=program_code[:4]
        ).distinct().order_by('class_group_name')
    
        # Log the filtered class groups for debugging
        print(f"Filtered class groups for program code {program_code[:4]}: {class_groups}")
    
        if not class_groups.exists():
            raise Http404("No class groups found.")
    
        serializer = ResultClassGroupSerializer(class_groups, many=True)
        class_groups_data = serializer.data
    
        for class_group in class_groups_data:
            # Get the instructor assigned to the course in the specific class group
            timetable_entry = ResultTimetable.objects.filter(
                result_identification=result_identification,
                class_group_id=class_group['class_group_id'],
                course_id=course.course_id
            ).first()
            print(f"Timetable entry for class group {class_group['class_group_id']}: {timetable_entry.__dict__ if timetable_entry else 'None'}")
        
            if timetable_entry:
                instructor_id = timetable_entry.instructor_id if timetable_entry.instructor else None
                print(f"Timetable entry for class group {class_group['class_group_id']}: {instructor_id}")
        
                if timetable_entry.instructor:
                    instructor_name = timetable_entry.instructor.get_full_name().title()
                    class_group['instructor_id'] = instructor_id
                    class_group['message'] = f"The assigned course for {class_group['class_group_name']} has already been assigned to {instructor_name}."
                else:
                    class_group['instructor_id'] = None
                    class_group['message'] = None

            else:
                print(f"No timetable entry found for class group {class_group['class_group_id']}")
                class_group['instructor_id'] = None
                class_group['message'] = None
    
        return Response({'class_groups': class_groups_data})

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class FilteredCoursesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, result_identification, program_id, *args, **kwargs):
        courses = ResultCourse.objects.filter(
            result_identification=result_identification,
            program_id=program_id
        )
        
        if not courses.exists():
            raise Http404("No courses found.")
        
        serializer = ResultCourseSerializer(courses, many=True)
        return Response({'courses': serializer.data})

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class FilteredCoursesByYearLevelAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, result_identification, program_id, year_level, *args, **kwargs):
        courses = ResultCourse.objects.filter(
            result_identification=result_identification,
            program_id=program_id,
            year_level=year_level
        )
        
        if not courses.exists():
            raise Http404("No courses found.")
        
        serializer = ResultCourseSerializer(courses, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@login_required
def get_classroom_vacant_times_api(request, result_identification, classroom_id):
    try:
        result_identification = get_object_or_404(ResultIdentification, result_id=result_identification)
        timetable_data = classroom_timetable(classroom_id, result_identification.result_id)['classroom_timetable']

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        vacant_times = get_vacant_time_slots(timetable_data, days)

        return Response(vacant_times, status=status.HTTP_200_OK)
    except ResultIdentification.DoesNotExist:
        return Response({'error': 'ResultIdentification not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@login_required
def get_instructor_timetable_api(request, result_identification, instructor_id):
    try:
        timetable_data = instructor_timetable(instructor_id, result_identification)
        instructor_timetable_data = timetable_data['instructor_timetable']

        extracted_data = [
            {
                'course_description': item['course_description'],
                'meeting_time': item['meeting_time'].split(', '),
                'meeting_day': item['meeting_day'].split(', '),
                'message': (
                    f"The selected time conflicts with {item['course_description']}, {item['meeting_time']}, "
                    f"{', '.join(item['meeting_day'].split(', ')[:-1])} and {item['meeting_day'].split(', ')[-1]}"
                    if len(item['meeting_day'].split(', ')) > 1
                    else f"The selected time conflicts with {item['course_description']}, {item['meeting_time']}"
                )
            }
            for item in instructor_timetable_data
        ]

        return Response({'instructor_timetable': extracted_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@login_required
def get_class_group_timetable_api(request, result_identification, class_group_id, course_id):

        timetable_data = class_group_timetable(class_group_id, result_identification)
        class_group_timetable_data = [
            
            {
                'course_name': item['course_code'],
                'course_id': item.get('course_id', ''),
                'course_description': item.get('course_description', ''),
                'instructor_name': item.get('instructor_name', ''),
                'instructor_id': item.get('instructor_id', ''),
                'class_group_name': item.get('class_group_name', ''),
                'class_group_id': item.get('class_group_id', ''),
                'classroom_name': item['room_name'],
                'room_id': item.get('room_id', ''),
                'learning_mode': 'Online' if item.get('is_online_class', False) else 'Face-to-face',
                'meeting_day': item.get('meeting_day', ''),
                'meeting_day_and_time': item['schedule'][0] if item['schedule'] else '',
                'meeting_id': item.get('meeting_id', ''),
                'timetable_result_id': item.get('timetable_result_id', ''),
                'result_timetable_detail_id': item.get('result_timetable_detail_id', ''),
                'start_time': item.get('start_time', ''),
                'end_time': item.get('end_time', '')
            }
            for item in timetable_data['class_group_timetable']
            if item.get('class_group_id') == class_group_id and item.get('course_id') == course_id
        ]
        print(class_group_timetable_data)
        return JsonResponse({'class_group_timetable': class_group_timetable_data}, status=status.HTTP_200_OK)

#==================================== DELETE ADMIN AND REP LOADS ====================================

class AdminLoadReleaseViewSet(viewsets.ModelViewSet):
    queryset = AdminLoadRelease.objects.all()
    serializer_class = AdminLoadReleaseSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['delete'])
    def delete_load(self, request, pk=None):
        if request.user.user_type not in [3, 4]:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            load = self.get_object()
            load.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AdminLoadRelease.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class REPLoadReleaseViewSet(viewsets.ModelViewSet):
    queryset = REPLoadRelease.objects.all()
    serializer_class = REPLoadReleaseSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['delete'])
    def delete_load(self, request, pk=None):
        if request.user.user_type not in [3, 4]:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            load = self.get_object()
            load.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except REPLoadRelease.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)