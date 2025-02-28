from django import forms
from apps.curriculum.models import Courses, Programs

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Programs
        fields = ['program_name', 'program_code']

class CoursesForm(forms.ModelForm):
    class Meta:
        model = Courses
        fields = ['course_code', 'course_description', 'year_level','semester','lecture', 'laboratory', 'program']