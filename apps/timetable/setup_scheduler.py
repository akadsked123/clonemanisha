from datetime import time
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
import requests
from apps.algorithm.tasks import run_genetic_algorithm
from apps.timetable.item_per_page_utils import validate_items_per_page
from apps.timetable.forms import NumberOfSetsPerYearLevelForm
from apps.timetable.models import  InitialSchedulerData
from apps.curriculum.models import Rooms, Programs
from django.contrib.auth.decorators import login_required
from apps.user.common.user_notification import create_notification
from apps.user.models import UserGroup
from apps.user.utils import get_template_by_user_type
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count, F, Q
import json
import os
import uuid
from django.conf import settings

# =====================================GENERATE SCHEDULE=====================================
class CustomJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, time):
      return obj.strftime('%H:%M')
    return super().default(obj)

@login_required
def scheduler(request):
    scheduler_data = InitialSchedulerData.objects.filter(program_id=request.user.program_id,institute_id=request.user.institute_id).only('scheduler_id', 'status', 'created_by', 'semester', 'academic_year')
    user_groups = UserGroup.objects.filter(program=request.user.program,institute=request.user.institute).annotate(total_members=Count('groupmember'),members_with_courses=Count('groupmember', filter=Q(groupmember__courses__isnull=False))).filter(total_members__gt=0,total_members=F('members_with_courses'))
    is_limit_reached = InitialSchedulerData.objects.filter(program_id=request.user.program_id,institute_id=request.user.institute_id,status__in=[2, 3]).exists()
    
    user_info_list = []
    initial_scheduler_data_ids = []
    items_per_page = request.GET.get('items_per_page', 25)
    page_number = request.GET.get('page', 1)

    # Validate pagination
    validated_items_per_page = validate_items_per_page(items_per_page, request, page_number)
    if isinstance(validated_items_per_page, HttpResponseRedirect):
        return validated_items_per_page

    paginator = Paginator(scheduler_data.order_by('-scheduler_id'), validated_items_per_page)
    paginated_scheduler_data = paginator.get_page(page_number)

    total_scheduler_data = scheduler_data.count()
    page_number = paginated_scheduler_data.number
    start_index = (page_number - 1) * paginator.per_page + 1

    if request.method == 'POST':
      if 'AbortScheduleGeneration' in request.POST:
         schedule = get_object_or_404(InitialSchedulerData, pk=id)
         pass
            
      if 'DeleteGeneratedSchedule' in request.POST:
          schedule_id = request.POST.get('schedule_id')
          schedule = get_object_or_404(InitialSchedulerData, pk=schedule_id)
          schedule.delete()
          messages.success(request, 'The selected data has been deleted successfully.')
          return redirect(request.get_full_path())             
      if 'GenerateScheduleSubmit' in request.POST:
          schedule_form = NumberOfSetsPerYearLevelForm(request.POST)
          if schedule_form.is_valid():
              user_group_id = request.POST.get('instructor-group')
              user_group = get_object_or_404(UserGroup, group_id=user_group_id)
              semester = user_group.semester
              academic_year = user_group.group_name

              number_of_classes = {
                  'first_year': schedule_form.cleaned_data.get('first_year_sets', 0),
                  'second_year': schedule_form.cleaned_data.get('second_year_sets', 0),
                  'third_year': schedule_form.cleaned_data.get('third_year_sets', 0),
                  'fourth_year': schedule_form.cleaned_data.get('fourth_year_sets', 0),
              }

              api_url = f"{settings.API_BASE_URL}/api/prepare-ga-data/{user_group_id}/"
              session = requests.Session()
              session.cookies.update(request.COOKIES)
              headers = {'Content-Type': 'application/json'}
              response = session.get(api_url, headers=headers)

              if response.status_code == 200:
                  try:
                      combined_data = response.json()
                      for level in combined_data.get('institute', {}).get('programs', [{}])[0].get('course_levels', []):
                          year_level = level.get('year_level')
                          if year_level == 1:
                              level['number_of_classes'] = number_of_classes['first_year']
                          elif year_level == 2:
                              level['number_of_classes'] = number_of_classes['second_year']
                          elif year_level == 3:
                              level['number_of_classes'] = number_of_classes['third_year']
                          elif year_level == 4:
                              level['number_of_classes'] = number_of_classes['fourth_year']

                      unique_id = uuid.uuid4()
                      file_name = f"initial-data-{unique_id}.json"
                      folder_path = os.path.join(settings.MEDIA_ROOT, 'scheduler_data')
                      os.makedirs(folder_path, exist_ok=True)
                      file_path = os.path.join(folder_path, file_name)

                      with open(file_path, 'w') as initial_data_json_file:
                          json.dump(combined_data, initial_data_json_file, indent=4)
                     
                      # Fetch total and active program counts for the institute and semester
                      total_programs = Programs.objects.filter(institute=user_group.institute).count()
                      active_program_count = InitialSchedulerData.objects.filter(institute=user_group.institute,semester=semester,status=2).count()

                      # Check if all programs have created initial data
                      if active_program_count + 1 == total_programs:

                          # Gather all active data for this semester
                          all_active_data = InitialSchedulerData.objects.filter(
                              institute=user_group.institute,
                              status__in=[2]
                          )
                          merged_data = {}
                          # Merge all active entries' data
                          for scheduler_entry in all_active_data:
                              try:
                                  with open(scheduler_entry.initial_data_json_file.path, 'r') as initial_data_json_file:
                                      program_data = json.load(initial_data_json_file)

                                      # get user who created the initial data for sending an email about the updates
                                      user = scheduler_entry.created_by
                                      user_id = user.id
                                      user_username = user.username
                                      user_email = user.email
                                      user_full_name = user.get_full_name()
                                      user_info_list.append((user_email, user_id, user_username, user_full_name))
                                      initial_scheduler_data_ids.append(scheduler_entry.scheduler_id)
                                      # Merge institute-level data
                                      if 'institute' in program_data:
                                          institute_data = program_data['institute']

                                          # If this is the first time, copy the institute data to merged_data
                                          if 'institute' not in merged_data:
                                              merged_data['institute'] = institute_data
                                          else:
                                              # Institute already exists, so merge the programs
                                              existing_programs = merged_data['institute'].get('programs', [])
                                              new_programs = institute_data.get('programs', [])

                                              # Merge program lists
                                              for new_program in new_programs:
                                                  existing_program = next((p for p in existing_programs if p['program_id'] == new_program['program_id']), None)
                                                  if existing_program:
                                                      existing_program.update(new_program)
                                                  else:
                                                      existing_programs.append(new_program)

                                              # Update the merged data's programs list
                                              merged_data['institute']['programs'] = existing_programs

                                          # Merge the instructors list
                                          existing_instructors = merged_data['institute'].get('instructors', [])
                                          new_instructors = institute_data.get('instructors', [])

                                          # Merge instructor lists
                                          for new_instructor in new_instructors:
                                              existing_instructor = next((i for i in existing_instructors if i['instructor_id'] == new_instructor['instructor_id']), None)
                                              if existing_instructor:
                                                  # Optionally, merge courses for the instructor
                                                  existing_courses = existing_instructor.get('courses', [])
                                                  new_courses = new_instructor.get('courses', [])
                                                  for new_course in new_courses:
                                                      if new_course not in existing_courses:
                                                          existing_courses.append(new_course)
                                                  existing_instructor['courses'] = existing_courses
                                              else:
                                                  # Append new instructor
                                                  existing_instructors.append(new_instructor)

                                          # Update the merged data's instructors list
                                          merged_data['institute']['instructors'] = existing_instructors

                              except (json.JSONDecodeError, FileNotFoundError) as e:
                                  messages.error(request, f"Error reading data for {scheduler_entry.program}: {e}")
                                  return redirect(request.get_full_path())

                          # Also include the new data from this program
                          if 'institute' in combined_data:
                              institute_data = combined_data['institute']
                              existing_programs = merged_data['institute'].get('programs', [])
                              new_programs = institute_data.get('programs', [])

                              # Merge the new program's data
                              for new_program in new_programs:
                                  existing_program = next((p for p in existing_programs if p['program_id'] == new_program['program_id']), None)
                                  if existing_program:
                                      existing_program.update(new_program)
                                  else:
                                      existing_programs.append(new_program)

                              merged_data['institute']['programs'] = existing_programs

                              # Merge the instructors data
                              existing_instructors = merged_data['institute'].get('instructors', [])
                              new_instructors = institute_data.get('instructors', [])

                              for new_instructor in new_instructors:
                                  existing_instructor = next((i for i in existing_instructors if i['instructor_id'] == new_instructor['instructor_id']), None)
                                  if existing_instructor:
                                      existing_courses = existing_instructor.get('courses', [])
                                      new_courses = new_instructor.get('courses', [])
                                      for new_course in new_courses:
                                          if new_course not in existing_courses:
                                              existing_courses.append(new_course)
                                      existing_instructor['courses'] = existing_courses
                                  else:
                                      existing_instructors.append(new_instructor)

                              merged_data['institute']['instructors'] = existing_instructors
                          
                          # Include the classrooms data
                          classrooms = Rooms.objects.all().values('room_id', 'room_name', 'is_lab')
                          merged_data['institute']['classrooms'] = list(classrooms)

                          meeting_time_file_path = os.path.join(settings.MEDIA_ROOT, 'meeting_time.json')
                          with open(meeting_time_file_path, 'r') as meeting_time_file:
                              meeting_data = json.load(meeting_time_file)
                          merged_data['institute']['timetable'] = meeting_data.get('timetable', [])
                          merged_data['institute']['classroom_timetable'] = meeting_data.get('classroom_timetable', [])
                          # Save the merged data into a new file
                          merged_unique_id = uuid.uuid4()
                          merged_file_name = f"final-data-{merged_unique_id}.json"
                          merged_file_path = os.path.join(folder_path, merged_file_name)

                          with open(merged_file_path, 'w') as merged_json_file:
                            json.dump(merged_data, merged_json_file, indent=4, cls=CustomJSONEncoder)

                          all_active_data.update(status=3)

                          # Save the new merged InitialSchedulerData entry
                          new_initial_scheduler_data = InitialSchedulerData.objects.create(
                              created_by=request.user,
                              semester=semester,
                              academic_year=academic_year,
                              program=request.user.program,
                              institute=request.user.institute,
                              initial_data_json_file=f'scheduler_data/{file_name}',
                              status=3
                          )
                          initial_scheduler_data_ids.append(new_initial_scheduler_data.scheduler_id)
                          final_user_email = request.user.email
                          final_user_id = request.user.id
                          final_user_username = request.user.username
                          final_user_full_name = request.user.get_full_name()
                          user_info_list.append((final_user_email, final_user_id, final_user_username, final_user_full_name))
                          run_genetic_algorithm.delay(merged_file_path, user_info_list, initial_scheduler_data_ids)
                          messages.info(request, "You will be notified once it's completed.")

                          create_notification(
                            recipient=request.user,
                            message="You will be notified soon once the schedule is completed.",
                            status=1,
                            sender=request.user,
                            notification_url=f'/user/notification/{request.user.username}'
                          )
                          return redirect(request.get_full_path())

                      else:
                          InitialSchedulerData.objects.create(
                              created_by=request.user,
                              semester=semester,
                              academic_year=academic_year,
                              program=request.user.program,
                              institute=request.user.institute,
                              initial_data_json_file=f'scheduler_data/{file_name}',
                              status=2
                          )

                          create_notification(
                            recipient=request.user,
                            message="The system is currently waiting for the other program chairpersons within your institute to finalize their data configurations. Once completed, schedule generation will begin automatically.",
                            status=1,
                            sender=request.user,
                            notification_url=f'/user/notification/{request.user.username}'
                          )

                          messages.info(request, "The system is currently waiting for the other program chairpersons within your institute to finalize their data configurations. Once completed, schedule generation will begin automatically.")
                          return redirect(request.get_full_path())
                      
                  except json.JSONDecodeError:
                      messages.error(request, "Failed to process the JSON data.")
                      return redirect(request.get_full_path())

              messages.error(request, "Failed to process the JSON data.")
              return redirect(request.get_full_path())
    else:
        schedule_form = NumberOfSetsPerYearLevelForm()
        
    template = get_template_by_user_type(request.user, 'scheduler')
    programs = Programs.objects.all()
    if template and request.user.user_type == 4:
        return render(request, template, {
            'schedule_form': schedule_form,
            'programs': programs,
            'user_groups': user_groups,
            'scheduler_data': paginated_scheduler_data,
            'total_scheduler_data': total_scheduler_data,
            'start_index': start_index,
            'items_per_page': items_per_page,
            'is_limit_reached': is_limit_reached,
        })

    raise Http404