from django.http import Http404
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from apps.institutes.forms import InstitutesForm
from .models import Institutes
from apps.curriculum.models import Programs
from apps.user.utils import get_template_by_user_type

@login_required
def institute(request):
     #Add Institute
    if request.method == 'POST':
        form = InstitutesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('institutes:list-of-institute')
    else:
        form = InstitutesForm()

    institutes = Institutes.objects.all()
    template = get_template_by_user_type(request.user, 'institutes')
    if template and request.user.user_type in [1,2]:
        return render(request, template, {'institutes': institutes})
    raise Http404

@login_required
def assign_faculty(request):
    template = get_template_by_user_type(request.user, 'assign-faculty')
    if template and request.user.user_type in [1,2]:
        return render(request, template)
    raise Http404