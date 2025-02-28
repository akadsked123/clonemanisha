from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from apps.curriculum.models import Courses, CurriculumYear
from apps.timetable.item_per_page_utils import validate_items_per_page
from apps.timetable.users_list_utils import get_users_list
from apps.user.common.group_members_utils import get_faculty_and_staff_info
from apps.user.forms import UserGroupForm
from apps.user.models import GroupMember, User, UserGroup
from apps.user.utils import get_template_by_user_type
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

@login_required
def instructors(request):
    template = get_template_by_user_type(request.user, 'instructors')
    user_info = get_faculty_and_staff_info(request)
    users_list = get_users_list(request)
    items_per_page = request.GET.get('items_per_page', 25)
    page_number = request.GET.get('page', 1)
    group_id = request.GET.get('group', None)

    # Get all user groups that have members and all members have courses
    user_groups = UserGroup.objects.filter(
        program=request.user.program,
        institute=request.user.institute
    )

    validated_items_per_page = validate_items_per_page(items_per_page, request, page_number, group_id)
    if isinstance(validated_items_per_page, HttpResponseRedirect):
        return validated_items_per_page
    
    if request.method == 'POST':
        if 'CreateGroupSubmit' in request.POST:
            user_group_form = UserGroupForm(request.POST)
            if user_group_form.is_valid():
                current_user = request.user
                # Retrieve the current user's program and institute
                current_program = current_user.program
                current_institute = current_user.institute
                
                # Check if a group with the same name, program, and institute already exists
                group_name = user_group_form.cleaned_data['group_name']
                semester = user_group_form.cleaned_data['semester']
                curriculum = user_group_form.cleaned_data['curriculum']

                if UserGroup.objects.filter(
                    group_name=group_name,
                    program=current_program,
                    institute=current_institute,
                    semester=semester,
                    curriculum=curriculum,
                ).exists():
                    messages.error(request, f'{group_name.upper()} for the {dict(UserGroup.SEMESTER_CHOICES).get(semester).upper()} already exists')
                    return redirect(request.get_full_path())
                
                # Set the program and institute fields before saving
                user_group = user_group_form.save(commit=False)
                user_group.program = current_program
                user_group.institute = current_institute
                user_group.save()
                
                messages.success(request, f'{group_name.upper()} for the {dict(UserGroup.SEMESTER_CHOICES).get(semester).upper()} in {curriculum.curriculum_year.upper()} has been created successfully.')
                return redirect(f"{request.path}?group={user_group.group_id}&page={page_number}&items_per_page={items_per_page}")
            else:
                messages.error(request, "Error creating the group.")
        else:
            user_group_form = UserGroupForm()

        if 'RemoveInstructorSubmit' in request.POST:
            member_id = request.POST.get('member_id')
            group_member = get_object_or_404(GroupMember, member_id=member_id)
            group_member.delete()
            messages.success(request, f"{group_member.user.first_name.upper()} {group_member.user.last_name.upper()} has been removed from {group_member.group.group_name.upper()}.")
            return redirect(f"{request.path}?group={group_member.group.group_id}&page={page_number}&items_per_page={items_per_page}")
        
        if 'RenameGroupSubmit' in request.POST:
            group_id = request.POST.get('group_id')
            new_group_name = request.POST.get('group_name')
            
            user_group = get_object_or_404(UserGroup, pk=group_id)
            user_group.group_name = new_group_name
            user_group.save()
            
            messages.success(request, 'Group name updated successfully.')
            return redirect(request.get_full_path())

        if 'RemoveAllInstructorSubmit' in request.POST:
            member_ids = request.POST.get('instructor_ids', '')
            member_ids = [int(id) for id in member_ids.split(',') if id.isdigit()]
            if member_ids:
                members = GroupMember.objects.filter(member_id__in=member_ids)
                deleted_count = 0
                for member in members:
                    member.delete()
                    deleted_count += 1

                if deleted_count > 0:
                    messages.success(request, f"{deleted_count} instructors(s) have been deleted successfully.")

            return redirect(request.get_full_path())

        if 'AddInstructorSubmit' in request.POST:
            group_id = request.POST.get('group_id')
            instructors = request.POST.getlist('instructor')

            if not group_id or not instructors:
                messages.error(request, "Inavlid request")
                return redirect(f"{request.path}?group={group_id}&page={page_number}&items_per_page={items_per_page}")

            try:
                group = get_object_or_404(UserGroup, group_id=group_id)
                for instructor_id in instructors:
                    instructor = get_object_or_404(User, id=instructor_id)
                    default_program = instructor.program
                    default_institute = instructor.institute 
                    GroupMember.objects.create(
                        group=group,
                        user=instructor,
                        program=default_program,
                        institute=default_institute,
                    )
                messages.success(request, f"{len(instructors)} instructor(s) have been added to the group.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

            return redirect(f"{request.path}?group={group_id}&page={page_number}&items_per_page={items_per_page}")
        
        if 'AssignCourseSubmit' in request.POST:
            group_id = request.POST.get('group_id')
            member_id = request.POST.get('instructor_id')
            curriculum_id = request.POST.get('curriculum_id')
            selected_course_ids = request.POST.getlist('selected_course_id')

            if not group_id or not member_id or not curriculum_id:
                messages.error(request, "Invalid request")
                return redirect(request.get_full_path())

            try:
                group = get_object_or_404(UserGroup, group_id=group_id)
                courses = Courses.objects.filter(course_id__in=selected_course_ids, curriculum_id=curriculum_id)
                group_member = get_object_or_404(GroupMember, member_id=member_id)
                existing_courses = group_member.courses.filter(curriculum_id=curriculum_id)

                courses_to_add = courses.exclude(course_id__in=existing_courses.values_list('course_id', flat=True))
                courses_to_remove = existing_courses.exclude(course_id__in=courses.values_list('course_id', flat=True))

                if courses_to_add:
                    group_member.courses.add(*courses_to_add)
                
                if courses_to_remove:
                    group_member.courses.remove(*courses_to_remove)
                messages.success(request, f"Successfully updated for {group_member.user.first_name.upper()} {group_member.user.last_name.upper()}.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

            return redirect(request.get_full_path())
        
        if 'CopyInstructorSubmit' in request.POST:
            selected_instructors = request.POST.getlist('selected_instructors[]')
            target_group_id = request.POST.get('target_group_id')

            if selected_instructors and target_group_id:
                target_group = get_object_or_404(UserGroup, group_id=target_group_id)

                copied_count = 0
                existing_count = 0
                semester_mismatch_count = 0

                # Fetch existing instructor IDs in the target group
                existing_instructors = GroupMember.objects.filter(group=target_group).values_list('user__id', flat=True)

                with transaction.atomic():
                    for member_id in selected_instructors:
                        instructor = get_object_or_404(GroupMember, member_id=member_id)

                        # Fetch source group of the instructor
                        source_group = instructor.group

                        # Check if the instructor already exists in the target group
                        if instructor.user.id not in existing_instructors:
                            # Create a new GroupMember instance for the target group
                            new_member = GroupMember(
                                group=target_group,
                                user=instructor.user,
                                program=instructor.program,
                                institute=instructor.institute,
                                date_assigned=instructor.date_assigned,
                                date_added=instructor.date_added
                            )
                            new_member.save()
                            copied_count += 1  # Increment copied count for new member

                            # Only copy courses if the semesters match
                            if source_group.semester == target_group.semester:
                                new_member.courses.set(instructor.courses.all())
                            else:
                                semester_mismatch_count += 1  # Increment the mismatch counter
                        else:
                            existing_count += 1

                # Prepare messages based on counts
                if copied_count > 0:
                    messages.success(request, f"{copied_count} instructor(s) copied successfully!")

                if existing_count > 0:
                    messages.warning(request, f"{existing_count} instructor(s) already exist.")

                # Display a general message for semester mismatches if there are any
                if semester_mismatch_count > 0:
                    messages.warning(request, f"Courses not copied for {semester_mismatch_count} instructor(s) due to semester mismatch.")

                # If no instructors were copied, existing, or had mismatches, display an informative message
                if copied_count == 0 and existing_count == 0 and semester_mismatch_count == 0:
                    messages.info(request, "No instructors were copied. Please check your selections and try again.")

                return redirect(request.get_full_path())

            messages.error(request, "Invalid request")
            return redirect(request.get_full_path())


    current_user = request.user
    curriculum_choices = CurriculumYear.objects.filter(
      institute=current_user.institute,
      program=current_user.program
    ).annotate(course_count=Count('courses')).filter(course_count__gt=0)
    selected_instructor_ids = GroupMember.objects.filter(group__in=user_groups).values_list('user_id', flat=True)
    
    if template and request.user.user_type in [4]:
        return render(request, template, {
            **user_info,
            **users_list,
            'semester_choices': UserGroup.SEMESTER_CHOICES,
            'curriculum_choices': curriculum_choices,
            'user_groups': user_groups,
            'selected_instructor_ids': selected_instructor_ids,
            'groupmembers': GroupMember.objects.filter(group__in=user_groups),
        })
    
    raise Http404