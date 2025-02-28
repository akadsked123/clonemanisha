from collections import defaultdict
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from apps.curriculum.forms import CopyCurriculumForm, ProgramForm
from apps.curriculum.forms import  CurriculumYearForm
from apps.curriculum.models import CurriculumYear, Programs, Courses
from django.contrib.auth.decorators import login_required
from apps.institutes.models import Institutes
from apps.user.utils import get_template_by_user_type
from django.db.models import Count
from django.db import IntegrityError

# ============================================= START FOR REGISTRAR VIEW =============================================
@login_required
def edit_institute(request):
    template = get_template_by_user_type(request.user, 'edit-institute')
    institutes = Institutes.objects.all()
    
    if 'UpdateInstituteSubmit' in request.POST:
        updated_institutes = []
        for institute in institutes:
            institute_id = request.POST.get(f'institute_id_{institute.institute_id}')
            institute_code = request.POST.get(f'acronym_{institute.institute_id}')
            institute_name = request.POST.get(f'institute_name_{institute.institute_id}')
            
            if institute_id and institute_code and institute_name:
                # Generate slug from institute name
                new_slug = slugify(institute_name)
                
                # Check if there are any changes to the institute's data
                if (
                    institute.acronym != institute_code or
                    institute.institute_name != institute_name or
                    institute.institute_slug != new_slug
                ):
                    institute.acronym = institute_code
                    institute.institute_name = institute_name
                    institute.institute_slug = new_slug
                    updated_institutes.append(institute)
        
        if updated_institutes:
            # Update only if there are changes
            Institutes.objects.bulk_update(updated_institutes, ['acronym', 'institute_name', 'institute_slug'])
            messages.success(request, 'Institutes updated successfully.')
        else:
            messages.info(request, 'No updates were made.')
    
        return redirect('curriculum:curriculum_maintenance_and_management')
    
    if template and request.user.user_type in [1]:
        return render(request, template, {'institutes': institutes})
    raise Http404("Access denied")


def group_courses_by_year_and_semester(courses):
    grouped_courses = defaultdict(lambda: defaultdict(list))
    totals = defaultdict(lambda: defaultdict(lambda: {'lecture': 0, 'lab': 0, 'credit_units': 0}))
    overall_totals = {'lecture': 0, 'lab': 0, 'credit_units': 0, 'courses': 0}

    for course in courses:
        year_level_display = {
            1: 'First Year',
            2: 'Second Year',
            3: 'Third Year',
            4: 'Fourth Year',
        }.get(course.year_level, f'Year {course.year_level}')

        semester_display = {
            1: '1st Semester',
            2: '2nd Semester',
            3: '3rd Semester',
        }.get(course.semester, f'{course.semester}th Semester')

        grouped_courses[year_level_display][semester_display].append(course)
        totals[year_level_display][semester_display]['lecture'] += course.lecture
        totals[year_level_display][semester_display]['lab'] += course.laboratory
        totals[year_level_display][semester_display]['credit_units'] += course.credit_units
        overall_totals['lecture'] += course.lecture
        overall_totals['lab'] += course.laboratory
        overall_totals['credit_units'] += course.credit_units
        overall_totals['courses'] += 1

    return grouped_courses, totals, overall_totals

@login_required
def curriculum_maintenance_and_management(request):
    # Get the template based on user type
    template = get_template_by_user_type(request.user, 'programs')
    # Fetch all institutes with related programs
    institutes = Institutes.objects.prefetch_related('programs_set').all()

    # Determine the most recent curriculum ID for each program
    for institute in institutes:
        for program in institute.programs_set.all():
            curriculum_with_courses = CurriculumYear.objects.filter(
                courses__program=program
            ).order_by('-curriculum_id').first()
            
            if curriculum_with_courses:
                program.curriculum_id = curriculum_with_courses.curriculum_id
            else:
                # No curriculum found, set a flag or handle accordingly
                program.curriculum_id = None  # Or set to a default value if needed
                
    if request.method == 'POST':
        program_form = ProgramForm(request.POST)

        # Handle program submission
        if 'AddProgramSubmit' in request.POST:
            if program_form.is_valid():
                program = program_form.save()
                institute = get_object_or_404(Institutes, pk=program.institute.pk)
                messages.success(request, f'Program successfully added to {institute.institute_name}.')
                return redirect(request.path)
            else:
                messages.error(request, 'An unexpected error occurred while adding a program.')
                return redirect(request.path)
        
        # Handle institute submission
        elif 'AddInstituteSubmit' in request.POST:
            new_institute_code = request.POST.get('institute_code')
            new_institute_name = request.POST.get('institute_name')
            
            if new_institute_code and new_institute_name:
                new_institute_slug = slugify(new_institute_name)
                
                # Check if an institute with the same acronym or name already exists
                if not Institutes.objects.filter(acronym=new_institute_code, institute_name=new_institute_name).exists():
                    # Create and save the new institute
                    new_institute = Institutes(
                        acronym=new_institute_code,
                        institute_name=new_institute_name,
                        institute_slug=new_institute_slug
                    )
                    new_institute.save()
                    messages.success(request, 'New institute created successfully.')
                else:
                    messages.error(request, 'An institute with this code or name already exists.')
            else:
                messages.error(request, 'Both institute code and name are required.')
            return redirect(request.path)

    else:
        program_form = ProgramForm()

    if template and request.user.user_type in [1]:
        context = {
            'institutes': institutes,
            'program_form': program_form,
        }
        return render(request, template, context)

    return HttpResponseForbidden("Access denied")

def change_program_name(program_id, program_code, program_name):
    program = Programs.objects.get(pk=program_id)
    program.program_code = program_code
    program.program_name = program_name
    program.save()
    return {'success': True}

def update_course(course_id, course_code, course_description, lecture, laboratory, semester, year_level):
    course = get_object_or_404(Courses, course_id=course_id)
    course.course_code = course_code
    course.course_description = course_description
    course.lecture = lecture
    course.laboratory = laboratory
    course.semester = semester
    course.year_level = year_level
    course.save()
    return {'success': True}

def delete_course(course_id):
    course = get_object_or_404(Courses, course_id=course_id)
    course.delete()
    return {'success': True}


def construct_curriculum_url(institute_slug, program_slug, curriculum_id):
    if institute_slug:
        url = reverse('curriculum:view_program_detail', kwargs={
            'institute_slug': institute_slug,
            'program_slug': program_slug
        })
    else:
        url = reverse('curriculum:curriculum', kwargs={
            'program_slug': program_slug
        })
    return f"{url}?curriculum={curriculum_id}"

@login_required
def view_program_detail(request, institute_slug, program_slug):
    template = get_template_by_user_type(request.user, 'view-program-detail')
    institute = get_object_or_404(Institutes, institute_slug=institute_slug)
    program = get_object_or_404(Programs, program_slug=program_slug, institute=institute)
    current_curriculum_id = request.GET.get('curriculum')
    program_id = program.pk
          
    if request.method == 'POST':
        if 'changeProgramNameSubmit' in request.POST:
            program_id = program.program_id
            program_code = request.POST.get('program_code')
            program_name = request.POST.get('program_name')

            # Check if the data has changed
            curriculum_id = request.GET.get('curriculum', '')
            if program.program_code == program_code and program.program_name == program_name:
                messages.info(request, 'No changes have been made.')
                return redirect(construct_curriculum_url(institute_slug, program_slug, curriculum_id))
            else:
                try:
                    update_result = change_program_name(program_id, program_code, program_name)
                    if update_result['success']:
                        messages.success(request, 'Successfully updated the program.')
                        return redirect(construct_curriculum_url(institute_slug, program_slug, curriculum_id))
                    else:
                        messages.error(request, 'Failed to update the program.')
                except IntegrityError as e:
                    error_message = str(e)
                    if 'Duplicate entry' in error_message:
                        if 'program_code' in error_message:
                            messages.error(request, f'Data is invalid due to duplication of program code: {program_code}.')
                        elif 'program_name' in error_message:
                            messages.error(request, f'Data is invalid due to duplication of program name: {program_name}.')
                    else:
                        messages.error(request, 'Failed to update the program.')
                  
        if 'editCourseSubmit' in request.POST:
          course_id = request.POST.get('course_id')
          course_code = request.POST.get('course_code')
          course_description = request.POST.get('course_description')
          lecture = int(request.POST.get('lecture', 0))
          laboratory = int(request.POST.get('laboratory', 0))
          semester = int(request.POST.get('semester', 1))
          year_level = int(request.POST.get('year_level', 1))

          # Fetch the existing course data
          course = get_object_or_404(Courses, course_id=course_id)

          if (course_code != course.course_code or
              course_description != course.course_description or
              lecture != course.lecture or
              laboratory != course.laboratory or
              semester != course.semester or
              year_level != course.year_level):

                # Update course if changes are detected
              update_result = update_course(course_id, course_code, course_description, lecture, laboratory, semester, year_level)

              if update_result['success']:
                  # Get the curriculum query parameter
                  curriculum_id = request.GET.get('curriculum', '')
                  messages.success(request, f'Successfully updated {course.course_code}.')
                  return redirect(construct_curriculum_url(institute_slug, program_slug, curriculum_id))
          else:
            messages.info(request, 'No changes have been made.')

        if 'deleteCourseSubmit' in request.POST:
                course_id = request.POST.get('course_id')
                if course_id:
                    result = delete_course(course_id)
                    if result['success']:
                        messages.success(request, 'Course successfully deleted.')
                    else:
                        messages.error(request, 'Failed to delete course.')
                else:
                    messages.error(request, 'No course ID provided.')
                
                # Redirect to the same page to avoid form resubmission issues
                curriculum_id = request.GET.get('curriculum', '')
                return redirect(construct_curriculum_url(institute_slug, program_slug, curriculum_id))
              
        if current_curriculum_id:
            try:
                CurriculumYear.objects.get(pk=current_curriculum_id)
            except CurriculumYear.DoesNotExist:
                messages.error(request, 'The selected curriculum year does not exist.')
                return redirect(request.path)
        
       # Initialize form
        if 'CopyCurriculumSubmit' in request.POST:
          copy_curriculum_form = CopyCurriculumForm(request.POST, program_id=program_id)
          
          if copy_curriculum_form.is_valid():
              source_curriculum = copy_curriculum_form.cleaned_data['source_curriculum']
              target_curriculum_year = copy_curriculum_form.cleaned_data['target_curriculum_year']

              # Ensure the program is valid
              try:
                  program = Programs.objects.get(pk=program_id)
              except Programs.DoesNotExist:
                  messages.error(request, 'The selected program does not exist.')
                  return redirect(request.path)

              # Ensure the source curriculum is related to the selected program
              if source_curriculum.program != program:
                  messages.error(request, 'The source curriculum does not belong to the selected program.')
                  return redirect(request.path)

              # Check if a curriculum year with the target name already exists
              if CurriculumYear.objects.filter(
                  curriculum_year=target_curriculum_year,
                  institute=source_curriculum.institute,
                  program=program
              ).exists():
                  messages.error(request, 'A curriculum year with this name already exists.')
                  return redirect(request.path)

              # Create the new curriculum year
              new_curriculum = CurriculumYear.objects.create(
                  curriculum_year=target_curriculum_year,
                  institute=source_curriculum.institute,
                  program=program  # Use the program object
              )

              # Copy the courses from the source curriculum to the new curriculum
              source_courses = Courses.objects.filter(curriculum=source_curriculum, program=program)
              for course in source_courses:
                  # Create a new course instance
                  new_course = Courses(
                      course_code=course.course_code,
                      course_description=course.course_description,
                      lecture=course.lecture,
                      laboratory=course.laboratory,
                      credit_units=course.credit_units,
                      semester=course.semester,
                      is_lab=course.is_lab,
                      year_level=course.year_level,
                      curriculum=new_curriculum,  # Assign the new curriculum year
                      program=program  # Assign the program
                  )
                  new_course.save()

              messages.success(request, f'Curriculum year "{source_curriculum.curriculum_year}" successfully copied to "{new_curriculum.curriculum_year}".')
              return redirect(construct_curriculum_url(institute_slug, program_slug, new_curriculum.pk))
          else:
              # Form is invalid, show errors
              messages.error(request, 'Invalid form submission.')
    else:
          # Initialize form without POST data
          copy_curriculum_form = CopyCurriculumForm(program_id=program_id)

    # Filter programs that have associated curriculum years with courses
    selected_programs = Programs.objects.filter(
        institute=institute,
        courses__curriculum__isnull=False
    ).distinct()

    # Filter curriculum years that have courses associated with the selected program
    curriculum_years = CurriculumYear.objects.filter(
        courses__program=program
    ).distinct()

    # Handle curriculum year selection
    selected_curriculum = request.GET.get('curriculum')
    if selected_curriculum:
        try:
            selected_curriculum = int(selected_curriculum)
            curriculum = get_object_or_404(CurriculumYear, pk=selected_curriculum)
            courses = Courses.objects.filter(program=program, curriculum=curriculum).order_by('year_level', 'semester')
            if not courses.exists():
                # Find the most recent previous curriculum year with courses
                previous_curriculum = CurriculumYear.objects.filter(
                    courses__program=program,
                    curriculum_id__lt=selected_curriculum
                ).order_by('-curriculum_id').first()

                if previous_curriculum:
                    # Redirect to the URL with the previous curriculum year
                    if program == curriculum.program:
                        messages.info(request, f'All courses of {curriculum.curriculum_year} have been deleted. Redirecting to the previous curriculum year: {previous_curriculum.curriculum_year}.')
                    return redirect(construct_curriculum_url(institute_slug, program_slug, previous_curriculum.curriculum_id))
                else:
                    # Find the next curriculum year with courses
                    next_curriculum = CurriculumYear.objects.filter(
                        courses__program=program,
                        curriculum_id__gt=selected_curriculum
                    ).order_by('curriculum_id').first()

                    if next_curriculum:
                        # Redirect to the URL with the next curriculum year
                        if program == curriculum.program:
                            messages.info(request, f'All courses of {curriculum.curriculum_year} have been deleted. Redirecting to the next curriculum year: {next_curriculum.curriculum_year}.')
                        return redirect(construct_curriculum_url(institute_slug, program_slug, next_curriculum.curriculum_id))
                    else:
                        # Redirect to the institute_and_programs page
                        if program == curriculum.program:
                            messages.info(request, 'No courses found. Please add courses to the curriculum.')
                        return redirect(reverse('curriculum:curriculum_maintenance_and_management'))
            else:
                selected_curriculum_name = curriculum.curriculum_year
        except (ValueError, CurriculumYear.DoesNotExist):
            return redirect(request.path)
    else:
        messages.error(request, 'No curriculum year matches the given query.')
        return redirect(reverse('curriculum:curriculum_maintenance_and_management'))

    # Group courses for display and calculate totals
    grouped_courses, totals, overall_totals = group_courses_by_year_and_semester(courses)
    
    grouped_courses = {k: dict(v) for k, v in grouped_courses.items()}
    totals = {k: dict(v) for k, v in totals.items()}
    current_url = request.get_full_path()

    if template and request.user.user_type in [1]:
        return render(request, template, {
            'program': program,
            'selected_programs': selected_programs,
            'grouped_courses': grouped_courses,
            'curriculum_years': curriculum_years,
            'selected_curriculum_name': selected_curriculum_name,
            'institute': institute,
            'totals': totals,
            'overall_totals': overall_totals,
            'current_url' : current_url,
            'copy_curriculum_form' : copy_curriculum_form,
        })

@login_required
def update_program_detail(request, institute_slug, program_slug):
    template = get_template_by_user_type(request.user, 'update-program-detail')
    institute = get_object_or_404(Institutes, institute_slug=institute_slug)
    program = get_object_or_404(Programs, program_slug=program_slug, institute=institute)
    
    # Update course details
    curriculum_id = request.GET.get('curriculum', '')
    if 'UpdateCourseSubmit' in request.POST:
        if request.method == 'POST':
            # Process the form data
            curriculum = get_object_or_404(CurriculumYear, curriculum_id=curriculum_id)
            course_ids = request.POST.getlist('course_id')
            course_codes = request.POST.getlist('course_code')
            course_descriptions = request.POST.getlist('course_description')
            lectures = request.POST.getlist('lecture')
            laboratories = request.POST.getlist('laboratory')
            semesters = request.POST.getlist('semester')
            year_levels = request.POST.getlist('year_level')

            # Fetch existing course IDs for the current curriculum, program, and institute
            existing_course_ids = set(
                Courses.objects.filter(
                    program=program, curriculum=curriculum
                ).values_list('course_id', flat=True)
            )
            submitted_course_ids = set(int(course_id) for course_id in course_ids if course_id)

            # Identify course IDs to delete (i.e., those that are not submitted)
            course_ids_to_delete = existing_course_ids - submitted_course_ids

            # Delete removed courses
            if course_ids_to_delete:
                Courses.objects.filter(
                    course_id__in=course_ids_to_delete, 
                    program=program, 
                    curriculum=curriculum
                ).delete()

            # Save or update courses
            for i in range(len(course_codes)):
                course_id = course_ids[i]
                course_data = {
                    'course_code': course_codes[i],
                    'course_description': course_descriptions[i],
                    'lecture': lectures[i],
                    'laboratory': laboratories[i],
                    'semester': semesters[i],
                    'year_level': year_levels[i],
                    'curriculum': curriculum,
                    'program': program
                }
                
                if course_id:
                    # Update existing course
                    Courses.objects.filter(id=course_id).update(**course_data)
                else:
                    # Create new course
                    Courses.objects.create(**course_data)
            
            selected_curriculum_name = curriculum.curriculum_year
            messages.success(request, f'Successfully updated {program.program_code} for {selected_curriculum_name}.')
            return redirect(construct_curriculum_url(institute_slug, program_slug, curriculum_id))
        else:
            messages.error(request, 'Invalid request method.')
    else:
        if request.method == 'POST':
            messages.error(request, 'Invalid request method.')
        courses = Courses.objects.none()
    # End for update course details

    # Handle curriculum year selection
    selected_curriculum = request.GET.get('curriculum')
    if selected_curriculum:
        try:
            selected_curriculum = int(selected_curriculum)
            # Fetch the curriculum year by its primary key
            curriculum = get_object_or_404(CurriculumYear, pk=selected_curriculum)
            # Ensure that the selected curriculum is associated with the program
            if Courses.objects.filter(program=program, curriculum=curriculum).exists():
                # Ensure 'year_level' and 'semester' are integers for proper ordering
                courses = Courses.objects.filter(program=program, curriculum=curriculum).order_by('year_level', 'semester')
                selected_curriculum_name = curriculum.curriculum_year
            else:
                courses = Courses.objects.none()# No courses for this curriculum and program
                selected_curriculum_name = curriculum.curriculum_year
        except (ValueError, CurriculumYear.DoesNotExist) as e:
            courses = Courses.objects.none()  # Empty queryset
            selected_curriculum_name = 'Select Curriculum Year'
    else:
        courses = Courses.objects.none()  # Empty queryset
        selected_curriculum_name = 'Select Curriculum Year'
    # End for handle curriculum year selection

    # Mapping for display strings
    year_level_display = {
        1: 'First Year',
        2: 'Second Year',
        3: 'Third Year',
        4: 'Fourth Year',
    }

    semester_display = {
        1: '1st Semester',
        2: '2nd Semester',
        3: '3rd Semester',
    }

    # Initialize defaultdicts for grouped courses and totals
    grouped_courses = defaultdict(lambda: defaultdict(list))

    # Process each course to populate grouped_courses and totals
    for course in courses:
        # Convert year_level and semester to display strings
        year_level_name = year_level_display.get(course.year_level, f'Year {course.year_level}')
        semester_name = semester_display.get(course.semester, f'{course.semester}th Semester')

        # Append the course to the appropriate group
        grouped_courses[year_level_name][semester_name].append(course)

    # Ensure all year levels and semesters are present in grouped_courses
    for year_level in sorted(year_level_display.values()):
        if year_level not in grouped_courses:
            grouped_courses[year_level] = {semester: [] for semester in semester_display.values()}           
        for semester in semester_display.values():
            if semester not in grouped_courses[year_level]:
                grouped_courses[year_level][semester] = []

    sorted_grouped_courses = dict(sorted(grouped_courses.items(), key=lambda x: list(year_level_display.values()).index(x[0])))          
    grouped_courses = {k: dict(v) for k, v in sorted_grouped_courses.items()}

    if template and request.user.user_type in [1]:
        return render(request, template, {
            'program': program,
            'grouped_courses': grouped_courses,
            'selected_curriculum_name': selected_curriculum_name,
            'institute': institute,
        })
    raise Http404("Access denied")
    
@login_required
def add_program_detail(request, institute_slug, program_slug):
    template = get_template_by_user_type(request.user, 'add-program-detail')
    institute = get_object_or_404(Institutes, institute_slug=institute_slug)
    program = get_object_or_404(Programs, program_slug=program_slug, institute=institute)
    
   # Create course details
    curriculum_id = request.GET.get('curriculum', '')
    if 'AddCourseSubmit' in request.POST:
        if request.method == 'POST':
            # Process the form data
            curriculum = get_object_or_404(CurriculumYear, curriculum_id=curriculum_id)
            course_codes = request.POST.getlist('course_code')
            course_descriptions = request.POST.getlist('course_description')
            lectures = request.POST.getlist('lecture')
            laboratories = request.POST.getlist('laboratory')
            semesters = request.POST.getlist('semester')
            year_levels = request.POST.getlist('year_level')

             # Prepare courses for bulk create
            courses_to_create = []
            for i in range(len(course_codes)):
                course_data = Courses(
                  program=program,
                  course_code=course_codes[i],
                  course_description=course_descriptions[i],
                  lecture=lectures[i],
                  laboratory=laboratories[i],
                  semester=semesters[i],
                  year_level=year_levels[i],
                  curriculum=curriculum
                )
                courses_to_create.append(course_data)

            # Bulk create courses
            if courses_to_create:
                Courses.objects.bulk_create(courses_to_create)
            selected_curriculum_name = curriculum.curriculum_year
            messages.success(request, f'Successfully added new courses for {program.program_code} in {selected_curriculum_name}.')
            return redirect(construct_curriculum_url(institute_slug, program_slug, curriculum_id))
        else:
            messages.error(request, 'Invalid request method.')
            courses = Courses.objects.none()
            
    copy_curriculum_form = CurriculumYearForm()
    if 'AddCurriculumYearSubmit' in request.POST:
      copy_curriculum_form = CurriculumYearForm(request.POST)
      if copy_curriculum_form.is_valid():
        curriculum_year = copy_curriculum_form.save(commit=False)
        curriculum_year.institute = institute
        curriculum_year.save()
        messages.success(request, f'{curriculum_year.curriculum_year} successfully added to {program.program_name}.')
        return redirect(request.path)
      else:
        print(f"Form is not valid: {copy_curriculum_form.errors}")
    else:
      copy_curriculum_form = CurriculumYearForm()
              
    # Get all programs for the given institute
    selected_programs = Programs.objects.filter(institute=institute).distinct()

    # Filter curriculum years to exclude those with associated courses and ensure they belong to the specified program and institute
    available_curriculum_years = CurriculumYear.objects.filter(
        institute=institute,
        program=program
    ).annotate(course_count=Count('courses')).filter(course_count=0).distinct()

    # Handle curriculum year selection
    selected_curriculum = request.GET.get('curriculum')
    if selected_curriculum:
      try:
          selected_curriculum = int(selected_curriculum)
          # Fetch the curriculum year by its primary key
          curriculum = get_object_or_404(CurriculumYear, pk=selected_curriculum)
          # Ensure that the selected curriculum is associated with the program and institute, and has no courses
          if curriculum.institute == institute and curriculum.program == program and not Courses.objects.filter(curriculum=curriculum).exists():
              # No courses for this curriculum and program
              courses = Courses.objects.none()
              selected_curriculum_name = curriculum.curriculum_year
          else:
              courses = Courses.objects.none()
              selected_curriculum_name = 'Select Curriculum Year'
              messages.info(request, 'If no curriculum years are available, please add a new curriculum year.')
      except (ValueError, CurriculumYear.DoesNotExist):
          courses = Courses.objects.none()
    else:
        courses = Courses.objects.none()
        selected_curriculum_name = 'Select Curriculum Year'

    year_level_display = {
        1: 'First Year',
        2: 'Second Year',
        3: 'Third Year',
        4: 'Fourth Year',
    }

    semester_display = {
        1: '1st Semester',
        2: '2nd Semester',
        3: '3rd Semester',
    }

    # Initialize defaultdicts for grouped courses and totals
    grouped_courses = defaultdict(lambda: defaultdict(list))

    # Process each course to populate grouped_courses and totals
    for course in courses:
        # Convert year_level and semester to display strings
        year_level_name = year_level_display.get(int(course.year_level), f'Year {course.year_level}')
        semester_name = semester_display.get(int(course.semester), f'{course.semester}th Semester')

        # Append the course to the appropriate group
        grouped_courses[year_level_name][semester_name].append(course)

    # Ensure all year levels and semesters are present in grouped_courses
    for year_level in year_level_display.values():
        if year_level not in grouped_courses:
            grouped_courses[year_level] = {semester: [] for semester in semester_display.values()}

        for semester in semester_display.values():
            if semester not in grouped_courses[year_level]:
                grouped_courses[year_level][semester] = []

    grouped_courses = {k: dict(v) for k, v in grouped_courses.items()}

    if template and request.user.user_type in [1]:
        return render(request, template, {
            'program': program,
            'selected_programs': selected_programs,
            'grouped_courses': grouped_courses,
            'available_curriculum_years': available_curriculum_years,
            'selected_curriculum_name': selected_curriculum_name,
            'institute': institute,
            'copy_curriculum_form': copy_curriculum_form,
        })
    
    raise Http404("Access denied")

# ============================================= END FOR REGISTRAR VIEW =============================================


# ============================================= START FOR PROGRAM CHAIRPERSON VIEW =============================================
# view curriculum for program chairperson
@login_required
def curriculum(request, program_slug):
    program = get_object_or_404(Programs, program_slug=program_slug, user=request.user)
    institute = get_object_or_404(Institutes, user=request.user)

    curriculum_with_courses = CurriculumYear.objects.filter(
      courses__program=program
    ).order_by('-curriculum_id').first()
    
    if curriculum_with_courses:
      request.session['curriculum_id'] = curriculum_with_courses.curriculum_id
      program.curriculum_id = curriculum_with_courses.curriculum_id
    else:
      # No curriculum found, set a flag or handle accordingly
      program.curriculum_id = None  # Or set to a default value if needed

    # Filter programs that have associated curriculum years with courses
    selected_programs = Programs.objects.filter(
        institute=institute,
        courses__curriculum__isnull=False
    ).distinct()

    # Filter curriculum years that have courses associated with the selected program
    curriculum_years = CurriculumYear.objects.filter(
        courses__program=program
    ).distinct()
    
    # Handle curriculum year selection
    selected_curriculum = request.GET.get('curriculum')
    if selected_curriculum:
        try:
            selected_curriculum = int(selected_curriculum)
            curriculum = get_object_or_404(CurriculumYear, pk=selected_curriculum)
            courses = Courses.objects.filter(program=program, curriculum=curriculum).order_by('year_level', 'semester')
            if not courses.exists():
                # Find the most recent previous curriculum year with courses
                previous_curriculum = CurriculumYear.objects.filter(
                    courses__program=program,
                    curriculum_id__lt=selected_curriculum
                ).order_by('-curriculum_id').first()

                if previous_curriculum:
                    # Redirect to the URL with the previous curriculum year
                    if program == curriculum.program:
                      return redirect(construct_curriculum_url(program_slug, previous_curriculum.curriculum_id))
                else:
                    # Find the next curriculum year with courses
                    next_curriculum = CurriculumYear.objects.filter(
                        courses__program=program,
                        curriculum_id__gt=selected_curriculum
                    ).order_by('curriculum_id').first()

                    if next_curriculum:
                        # Redirect to the URL with the next curriculum year
                        if program == curriculum.program:
                          return redirect(construct_curriculum_url(program_slug, next_curriculum.curriculum_id))
                    else:
                        # Redirect to the institute_and_programs page
                        if program == curriculum.program:
                          return redirect(reverse('curriculum:curriculum', kwargs={'program_slug': program_slug}))
            else:
                selected_curriculum_name = curriculum.curriculum_year
        except (ValueError, CurriculumYear.DoesNotExist):
            return redirect(request.path)
    else:
        messages.error(request, 'No curriculum year matches the given query.')
        return redirect(reverse('curriculum:curriculum', kwargs={'program_slug': program_slug}))

    # Group courses for display and calculate totals
    grouped_courses, totals, overall_totals = group_courses_by_year_and_semester(courses)

    grouped_courses = {k: dict(v) for k, v in grouped_courses.items()}
    totals = {k: dict(v) for k, v in totals.items()}
    current_url = request.get_full_path()

    # Fetch the template based on user type
    template = get_template_by_user_type(request.user, 'curriculum')

    # Only allow access if the user type matches program chairperson (assumed as 4)
    if template and request.user.user_type in [4]:
        return render(request, template, {
            'program': program,
            'selected_programs': selected_programs,
            'grouped_courses': grouped_courses,
            'curriculum_years': curriculum_years,
            'selected_curriculum_name': selected_curriculum_name,
            'institute': institute,
            'totals': totals,
            'overall_totals': overall_totals,
            'current_url' : current_url,
        })

    # If the conditions are not met, raise a 404
    raise Http404("Access denied")

# ============================================= END FOR PROGRAM CHAIRPERSON VIEW =============================================