from django import forms

from apps.institutes.models import Institutes
from .models import Programs, Rooms, Courses, CurriculumYear

class CurriculumYearForm(forms.ModelForm):
    class Meta:
        model = CurriculumYear
        fields = ['curriculum_year', 'program']

class RoomsForm(forms.ModelForm):
    class Meta:
        model = Rooms
        fields = ['room_name', 'is_lab']

class CoursesForm(forms.ModelForm):
    class Meta:
        model = Courses
        fields = ['course_code', 'course_description', 'lecture', 'laboratory', 'credit_units', 'semester','is_lab', 'year_level']

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Programs
        fields = ['program_code', 'program_name', 'institute']

class InstituteForm(forms.ModelForm):
  class Meta:
    model = Institutes
    fields = ['acronym', 'institute_name', 'institute_slug']

  def save(self, commit=True):
    instance = super().save(commit=False)
    instance.slug = instance.institute_name.lower().replace(" ", "-")
    if commit:
      instance.save()
    return instance
  
class CopyCurriculumForm(forms.Form):
    source_curriculum = forms.ModelChoiceField(
        queryset=CurriculumYear.objects.none(),  # Default to empty queryset
        label="Select Curriculum Year to Copy"
    )
    target_curriculum_year = forms.CharField(
        max_length=255,
        label="Copy To (New Curriculum Year)"
    )

    def __init__(self, *args, **kwargs):
        program_id = kwargs.pop('program_id', None)
        super().__init__(*args, **kwargs)
        if program_id:
            self.fields['source_curriculum'].queryset = CurriculumYear.objects.filter(
                courses__isnull=False,  # Ensure there are courses associated
                program_id=program_id  # Filter by program_id
            ).distinct()