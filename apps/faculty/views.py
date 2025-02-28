from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.curriculum.models import Programs
from apps.user.utils import get_template_by_user_type


@login_required
def faculty(request):
    programs = Programs.objects.all()
    template = get_template_by_user_type(request.user, 'faculty')
    if template and request.user.user_type == 2 or 3:
        return render(request, template, {'programs': programs})
    raise Http404

@login_required
def faculty_workload(request):
    template = get_template_by_user_type(request.user, 'faculty-workload')
    if template and request.user.user_type == 2:
        return render(request, template)
    raise Http404

@login_required
def assign_faculty(request):
    template = get_template_by_user_type(request.user, 'assign-faculty')
    if template and request.user.user_type == 3:
        return render(request, template)
    raise Http404
