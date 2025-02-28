from django.http import Http404
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from apps.programs.forms import CoursesForm, ProgramForm
from apps.curriculum.forms import CurriculumYearForm
from apps.curriculum.models import Courses, CurriculumYear, Programs
from apps.user.utils import get_template_by_user_type

@login_required
def programs(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programs:programs')
    else:
        form = ProgramForm()

    programs = Programs.objects.all()
    template = get_template_by_user_type(request.user, 'programs')
    if template and request.user.user_type == 2 or 3:
        return render(request, template, {'programs': programs, 'form': form})
    raise Http404

@login_required
def courses(request):
    if request.method == 'POST':
        form = CoursesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programs:courses')
    else:
        form = CoursesForm()

    courses = Courses.objects.all()
    template = get_template_by_user_type(request.user, 'courses')
    if template and request.user.user_type == 3:
        return render(request, template, {'courses': courses, 'form': form})
    raise Http404

@login_required
def curriculum_version(request):
    # Add Currilum Versions
    if request.method == 'POST':
        form = CurriculumYearForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programs:curriculum-version')
    else:
        form = CurriculumYearForm()
        
    curriculum_versions = CurriculumYear.objects.all()
    template = get_template_by_user_type(request.user, 'curriculum-version')
    if template and request.user.user_type == 3:
        return render(request, template, {'curriculum_versions': curriculum_versions, 'form': form})
    raise Http404



