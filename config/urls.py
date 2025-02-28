from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static 
from django.conf import settings
from apps.user.views import signup, verify_account
from config.views import AdminLoadReleaseViewSet, ClassGroupsAPI, ClassroomsAPI, CourseListAPIView, CoursesAPI, FilteredClassGroupsAPI, FilteredCoursesAPI, FilteredCoursesByYearLevelAPI, InitialSchedulerDataViewSet, InstructorsAPI, MeetingTimesAPI, NotificationListView, ProtectedMediaView, REPLoadReleaseViewSet, SchedulerDataAPIView, TimetableAPI, UserCoursesView, check_unique, get_class_group_timetable_api, get_classroom_vacant_times_api, get_instructor_timetable_api, home_redirect
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter

admin.site.site_title = 'administrator'

router = DefaultRouter()
router.register(r'admin-loads', AdminLoadReleaseViewSet)
router.register(r'rep-loads', REPLoadReleaseViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/signup/', signup, name='signup'),
    path('accounts/verify-account/', verify_account, name='verify-account'),
    path('accounts/', include('allauth.urls')),
    path('', home_redirect, name="home_redirect"),
    path('__reload__/', include('django_browser_reload.urls')), #remove this during production
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('curriculum/', include('apps.curriculum.urls', namespace='curriculum')),
    path('timetable/', include('apps.timetable.urls', namespace='schedules')),
    path('user/', include('apps.user.urls', namespace='user')),
    path('institute/', include('apps.institutes.urls', namespace='institutes')),
    path('program/', include('apps.programs.urls', namespace="programs")),
    path('faculty-and-staff/', include('apps.faculty.urls', namespace="faculty")),
    # path('algorithm/', views.algorithm_view, name='algorithm_view'),
    # path('course/', views.course_view, name='course_view'),
    path("__debug__/", include("debug_toolbar.urls")), #remove this during production
    path('check-unique/', check_unique, name='check_unique'),

    #Django Rest Framework
    path('api/courses/', CourseListAPIView.as_view(), name='course_list_api'),
    path('api/courses/<int:member_id>', UserCoursesView.as_view(), name='instructor_assigned_courses'),
    path('api/prepare-ga-data/<int:user_group_id>/', SchedulerDataAPIView.as_view(), name='prepare-ga-data'),
    path('api/notifications/', NotificationListView.as_view(), name='notification-list'),

    #Timetable Results
    path('api/v2/timetable/<int:result_identification>/', TimetableAPI.as_view(), name='timetable-results'),
    path('api/v2/classrooms/<int:result_identification>/', ClassroomsAPI.as_view(), name='classrooms_results'),
    path('api/v2/meeting-times/<int:result_identification>/', MeetingTimesAPI.as_view(), name='meeting_times_results'),
    path('api/v2/instructors/<int:result_identification>/', InstructorsAPI.as_view(), name='instructors_results'),
    path('api/v2/courses/<int:result_identification>/', CoursesAPI.as_view(), name='courses_results'),
    path('api/v2/courses/<int:result_identification>/<int:program_id>/', FilteredCoursesAPI.as_view(), name='filtered_courses_results'),
    path('api/v2/class-groups/<int:result_identification>/', ClassGroupsAPI.as_view(), name='year_levels_results'),
    path('api/v2/class-groups/<int:result_identification>/<int:year_level>/<int:course_id>/', FilteredClassGroupsAPI.as_view(), name='filtered_class_groups_api'),
    path('api/v2/classrooms/vacant-times/<int:result_identification>/<int:classroom_id>/', get_classroom_vacant_times_api, name='get_classroom_vacant_times_api'),
    path('api/v2/timetable/instructor/<int:result_identification>/<int:instructor_id>/', get_instructor_timetable_api, name='instructor-timetable-api'),
    path('api/v2/timetable/class-group/<int:result_identification>/<int:class_group_id>/<int:course_id>/', get_class_group_timetable_api, name='class-group-timetable-api'),
    path('api/v2/courses/<int:result_identification>/<int:program_id>/<int:year_level>', FilteredCoursesByYearLevelAPI.as_view(), name='filtered_courses_by_year_level_results'),
    path('api/progress/<int:pk>/', InitialSchedulerDataViewSet.as_view({'get': 'retrieve'})),

    #Protected Media
    path('media/<path:path>', login_required(ProtectedMediaView.as_view()), name='protected_media'),


    #Default Router
    path('api/v2/', include(router.urls)),
]   
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
