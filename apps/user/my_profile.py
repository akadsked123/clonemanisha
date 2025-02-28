from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from apps.timetable.models import GeneratedSchedule, ResultIdentification
from apps.timetable.schedule_instructor import instructor_timetable
from .forms import FacultyProfileForm
from .models import AdminLoadRelease, REPLoadRelease, User, FacultyProfile, UndergraduateDegree, GraduateDegree, Institutes, Programs

SEMESTER_MAPPING = {
        1: "FIRST SEMESTER",
        2: "SECOND SEMESTER",
        3: "THIRD SEMESTER"
    }

@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    faculty_profile, created = FacultyProfile.objects.get_or_create(user=request.user)
    admin_load_releases = AdminLoadRelease.objects.filter(user=user)
    if not admin_load_releases.exists():
        admin_load_releases = None
    
    rep_load_releases = REPLoadRelease.objects.filter(user=user)
    if not rep_load_releases.exists():
        rep_load_releases = None
    recent_result_identification = ResultIdentification.objects.order_by('-created_at').first()
    result_identification_id = recent_result_identification.result_id if recent_result_identification else None
    instructor_timetable_data = instructor_timetable(user_id, result_identification_id) if user_id and result_identification_id else {'instructor_timetable': []}
    
    if request.user.id != user.id:
        user = request.user
        url = reverse('user:my-profile', args=[user.id])
        return redirect(url)
    
    core_time = {}
    for entry in instructor_timetable_data['instructor_timetable']:
        for view in entry['timetable_view']:
            meeting_day = view['meeting_day']
            meeting_time = view['meeting_time']
            if meeting_day not in core_time:
                core_time[meeting_day] = set()
            core_time[meeting_day].add(meeting_time)

    core_time_str = ", ".join([f"{day}: {', '.join(sorted(times))}" for day, times in core_time.items()])

    generated_schedule = GeneratedSchedule.objects.filter(result_identification=result_identification_id).first()
    semester = generated_schedule.semester if generated_schedule else None
    academic_year = generated_schedule.academic_year if generated_schedule else None
    semester_str = SEMESTER_MAPPING.get(semester, "")
    core_time_label_str = f"({semester_str} - {academic_year})"

    institutes = Institutes.objects.all()
    programs = Programs.objects.all()

    if request.method == 'POST':
        form = FacultyProfileForm(request.POST, instance=faculty_profile)
        has_changed = False

        if form.is_valid():
            # Check if the form has changes
            if form.has_changed():
                form.save()
                has_changed = True

                # Update the User model if program, institute, or employment status has changed
                user_institute = form.cleaned_data.get('institute')
                user_program = form.cleaned_data.get('program')
                user_employment_status = form.cleaned_data.get('employment_status')

                if user.institute != user_institute or user.program != user_program or user.employment_status != user_employment_status:
                  user.institute = user_institute
                  user.program = user_program
                  user.employment_status = user_employment_status
                  user.save()
            
            # Process undergraduate degrees
            existing_undergraduate_degrees = set(faculty_profile.undergraduate_degrees.values_list('name', flat=True))
            new_undergraduate_degrees = set(
                value for key, value in request.POST.items()
                if key.startswith('undergraduate_degree_') and value
            )

            if existing_undergraduate_degrees != new_undergraduate_degrees:
                has_changed = True
                faculty_profile.undergraduate_degrees.clear()
                for degree_name in new_undergraduate_degrees:
                    degree, created = UndergraduateDegree.objects.get_or_create(name=degree_name)
                    faculty_profile.undergraduate_degrees.add(degree)
            
            # Process graduate degrees
            existing_graduate_degrees = set(faculty_profile.graduate_degrees.values_list('name', flat=True))
            new_graduate_degrees = set(
                value for key, value in request.POST.items()
                if key.startswith('graduate_degree_') and value
            )

            if existing_graduate_degrees != new_graduate_degrees:
                has_changed = True
                faculty_profile.graduate_degrees.clear()
                for degree_name in new_graduate_degrees:
                    degree, created = GraduateDegree.objects.get_or_create(name=degree_name)
                    faculty_profile.graduate_degrees.add(degree)
            
            # Display appropriate messages
            if has_changed:
                messages.success(request, 'Faculty profile updated successfully.')
            else:
                messages.info(request, 'No changes detected. No data has been saved.')
            
            return redirect('user:my-profile', user_id=user.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FacultyProfileForm(instance=faculty_profile)

    return render(request, './account/my_profile.html', {
        'user': user,
        'user_type': request.user.user_type,
        'faculty_profile': faculty_profile,
        'institutes': institutes,
        'programs': programs,
        'form': form,
        'admin_load_releases': admin_load_releases,
        'rep_load_releases': rep_load_releases,
        'core_time': core_time_str,
        'core_time_label': core_time_label_str,
    })