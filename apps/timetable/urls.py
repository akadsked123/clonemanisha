from django.urls import path

from apps.timetable import list_of_conflicts, my_schedule, schedule_class_group, schedule_classroom, schedule_instructor, setup_classroom, setup_scheduler
from apps.timetable import setup_instructor
from django.conf.urls.static import static
from django.conf import settings

from apps.timetable.print_schedule import generate_pdf
from apps.user import add_load_release

app_name = 'timetable'

urlpatterns = [
    path('scheduler/', setup_scheduler.scheduler, name='scheduler'),
    path('scheduler/classrooms/<int:result_identification>/', schedule_classroom.schedule_classrooms, name='scheduler-classrooms'),
    path('scheduler/instructors/<int:result_identification>/', schedule_instructor.schedule_instructors, name='scheduler-instructors'),
    path('scheduler/classgroups/<int:result_identification>/', schedule_class_group.schedule_class_groups, name='scheduler-class-groups'),
    path('scheduler/list-of-conflicts/<int:result_identification>/', list_of_conflicts.list_of_conflicts_view, name='list-of-conflicts'),
    path('print-schedule/<int:result_identification>/<int:selected_instructor_id>/', generate_pdf, name='generate_pdf'),
    path('classrooms/', setup_classroom.classrooms, name='rooms'),
    path('instructors/', setup_instructor.instructors, name='instructors'),
    path('instructors/add-load-release/<int:selected_instructor_id>/<int:group_id>/', add_load_release.add_load_Admin_REP_release, name='add_load_release'),
    path('my-schedule/', my_schedule.my_schedule, name='my-schedule'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

