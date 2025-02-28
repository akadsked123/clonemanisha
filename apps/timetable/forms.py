from django import forms

from apps.curriculum.models import Courses, Programs, Rooms
from apps.institutes.models import Institutes
from apps.timetable.models import ResultClassGroup, ResultClassroom
from apps.user.models import GroupMember, User

# Collect the semester and the number of sets for each year level
class NumberOfSetsPerYearLevelForm(forms.Form):
    first_year_sets = forms.IntegerField(label='First year', min_value=1, max_value=10, required=True)
    second_year_sets = forms.IntegerField(label='Second year', min_value=1, max_value=10, required=True)
    third_year_sets = forms.IntegerField(label='Third year', min_value=1, max_value=10, required=True)
    fourth_year_sets = forms.IntegerField(label='Fourth year', min_value=1, max_value=10, required=True)

class GroupMemberForm(forms.ModelForm):
    class Meta:
        model = GroupMember
        fields = ['user', 'program', 'institute', 'courses']

    def __init__(self, *args, **kwargs):
        # Accept the current group as a parameter when initializing the form
        current_group = kwargs.pop('current_group', None)
        super(GroupMemberForm, self).__init__(*args, **kwargs)

        # Filter users that are not already in the selected group
        if current_group:
            existing_members = GroupMember.objects.filter(group=current_group).values_list('user', flat=True)
            self.fields['user'].queryset = User.objects.exclude(id__in=existing_members)

        # Dynamically filter or customize fields if necessary
        self.fields['program'].queryset = Programs.objects.all()
        self.fields['institute'].queryset = Institutes.objects.all()
        self.fields['courses'].queryset = Courses.objects.all()

class RoomForm(forms.ModelForm):
    class Meta:
        model = Rooms
        fields = ['room_name', 'building', 'is_lab']

class ResultClassroomForm(forms.ModelForm):
    class Meta:
        model = ResultClassroom
        fields = ['room_name', 'is_lab']

class ResultClassGroupForm(forms.ModelForm):
    class Meta:
        model = ResultClassGroup
        fields = ['class_group_name', 'year_level']