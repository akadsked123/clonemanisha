from django import forms
from .models import Institutes

class InstitutesForm(forms.ModelForm):
    class Meta:
        model = Institutes
        fields = ['institute_name', 'acronym']
