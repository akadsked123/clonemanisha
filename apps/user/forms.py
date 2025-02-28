from django import forms
from .models import FacultyProfile, GraduateDegree, UndergraduateDegree, User, UserGroup
from allauth.account.forms import ChangePasswordForm as AllauthChangePasswordForm, SignupForm as AllauthSignupForm
from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation
from django import forms

class SignupForm(AllauthSignupForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    middle_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    suffix = forms.CharField(max_length=10, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'suffix', 'email', 'password1', 'password2')

    def save(self, request):
        user = super(SignupForm, self).save(request)
        send_email_confirmation(request, user, True)
        return user
    
#  Personal Information Forms
class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']

class CoverImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['cover_image']

class UpdatePersonalInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name',  'middle_name', 'suffix', 'gender', 'email','phone_number',]

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '')
        if phone_number is None:
            return ''
        phone_number = phone_number.replace('-', '')
        return phone_number
    
# Change Password
class RequestPasswordChangeForm(AllauthChangePasswordForm):
  otp = forms.CharField(max_length=6, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter OTP'}))
  send_otp = forms.BooleanField(required=False, widget=forms.HiddenInput)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Customize labels for inherited fields
    self.fields['oldpassword'].label = 'Old password'
    self.fields['password1'].label = 'New password'
    self.fields['password2'].label = 'Confirm new password'
    # Customizing field attributes if needed
    self.fields['oldpassword'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Old password'})
    self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'New password'})
    self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm new password'})


class UserGroupForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ['group_name', 'semester', 'curriculum']

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     original_name = instance.group_name.strip()
    #     counter = 1

    #     while UserGroup.objects.filter(group_name=instance.group_name).exists():
    #         instance.group_name = f"{original_name} ({counter})"
    #         counter += 1

    #     if commit:
    #         instance.save()
    #     return instance


class UndergraduateDegreeInlineForm(forms.ModelForm):
    class Meta:
        model = UndergraduateDegree
        fields = ['name']

class GraduateDegreeInlineForm(forms.ModelForm):
    class Meta:
        model = GraduateDegree
        fields = ['name']
        
class FacultyProfileForm(forms.ModelForm):
    undergraduate_degrees = forms.ModelMultipleChoiceField(
        queryset=UndergraduateDegree.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    graduate_degrees = forms.ModelMultipleChoiceField(
        queryset=GraduateDegree.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = FacultyProfile
        fields = ['academic_rank', 'undergraduate_degrees', 'graduate_degrees', 'employment_status', 'institute', 'program', 'designation', 'department', 'core_time', 'student_consultation_time', 'date_hired']