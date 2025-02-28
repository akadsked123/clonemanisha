import random
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.curriculum.models import Courses, CurriculumYear, Programs
from apps.institutes.models import Institutes
from apps.user.common.phone_validators import validate_ph_phone_number
from apps.user.common.account_compress_image import CoverImageField, ProfileImageField
from django.db.models.functions import Now
from django.db.models import ExpressionWrapper, DateTimeField
from datetime import timedelta

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50,blank=False,null=False)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50,blank=False,null=False)
    suffix = models.CharField(max_length=10, blank=True, null=True)
    profile_image = ProfileImageField(upload_to='profile_image/', null=True, blank=True)
    phone_number = models.CharField(max_length=11,validators=[validate_ph_phone_number],help_text="Enter a phone number in the format: 09-XXXXX-YYYY", blank=True, null=True)

    GENDER_CHOICES = (
        ('1', 'Male'),
        ('2', 'Female'),
        ('3', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=False, null=False)

    USER_TYPE_CHOICES = (
        (1, 'registrar'),
        (2, 'vpaa'),
        (3, 'dean'),
        (4, 'progchair'),
        (5, 'faculty')
    )
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, blank=False, null=False, default=5)
    
    EMPLOYMENT_STATUS_CHOICES = [
        (1, 'Permanent'),
        (2, 'Temporary'),
        (3, 'Casual'),
        (4, 'Contract of Service'),
        (5, 'Job Order'),
        (6, 'Coterminous'),
        (7, 'Contractual'),
    ]
    employment_status = models.IntegerField(choices=EMPLOYMENT_STATUS_CHOICES, blank=True, null=True)

    cover_images = [
        'cover_image/107012025191346.jpg',
        'cover_image/107012025225052.jpg',
        'cover_image/107012025225205.jpg',
        'cover_image/107012025225252.jpg',
        'cover_image/107012025225409.jpg',
        'cover_image/107012025225413.jpg',
        'cover_image/108012025005640.jpg',
        'cover_image/108012025013034.jpg',
        'cover_image/1610112024235135.jpg'
    ]
    cover_image = CoverImageField(upload_to='cover_image/', default=random.choice(cover_images))

    institute = models.ForeignKey(Institutes, on_delete=models.CASCADE, null=True, blank=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, null=True, blank=True)
    
    POSITION_CHOICES = [
        (1, 'Instructor I'),
        (2, 'Instructor II'),
        (3, 'Instructor III'),
        (4, 'Assistant Professor I'),
        (5, 'Assistant Professor II'),
        (6, 'Assistant Professor III'),
        (7, 'Assistant Professor IV'),
        (8, 'Associate Professor I'),
        (9, 'Associate Professor II'),
        (10, 'Associate Professor III'),
        (11, 'Associate Professor IV'),
        (12, 'Associate Professor V'),
        (13, 'Professor I'),
        (14, 'Professor II'),
        (15, 'Professor III'),
        (16, 'Professor IV'),
        (17, 'Professor V'),
        (18, 'Professor VI'),
        (19, 'College Professor'),
    ]
    position = models.IntegerField(choices=POSITION_CHOICES, blank=True, null=True)

    def save(self, *args, **kwargs):
      if not self.username:
          first_name_no_spaces = self.first_name.replace(" ", "")
          last_name_no_spaces = self.last_name.replace(" ", "")
          self.username = f"{first_name_no_spaces}{last_name_no_spaces}".lower()

      if not self.cover_image:
            self.cover_image = random.choice(self.cover_images)
      super().save(*args, **kwargs)


    def get_full_name(self):
        full_name = self.first_name
        if self.middle_name:
            full_name += f" {self.middle_name}"
        full_name += f" {self.last_name}"
        return full_name

    class Meta:  
        db_table = 'users'
        verbose_name = 'Faculty and Staff'
        verbose_name_plural = 'Faculty and Staff'

class UserGroup(models.Model):
    SEMESTER_CHOICES = [
        ('1', 'First Semester'),
        ('2', 'Second Semester'),
        ('3', 'Third Semester'),
    ]
    
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=255)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institutes, on_delete=models.CASCADE)
    curriculum = models.ForeignKey(CurriculumYear, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.group_name

    class Meta:
        db_table = 'user_groups'
        verbose_name = 'User Group'
        verbose_name_plural = 'User Groups'
        unique_together = ('group_name', 'program', 'institute', 'semester', 'curriculum')

class GroupMember(models.Model):
    member_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institutes, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Courses, blank=True)
    date_assigned = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.group.group_name}"

    class Meta:
        db_table = 'group_members'
        verbose_name = 'Group Member'
        verbose_name_plural = 'Group Members'
        unique_together = ('group', 'user')

class Notification(models.Model):
  STATUS_CHOICES = [
    (1, 'Unread'), 
    (2, 'Read'),
    (3, 'Dismissed'),
  ]
  notification_id = models.AutoField(primary_key=True)
  recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
  sender = models.ForeignKey(User, related_name='sent_notifications', null=True, blank=True, on_delete=models.SET_NULL)
  message = models.TextField()
  status = models.IntegerField(choices=STATUS_CHOICES, default=1)
  date_time = models.DateTimeField(default=timezone.now)
  created_at = models.DateTimeField(auto_now_add=True)
  dismissed_at = models.DateTimeField(null=True, blank=True)
  read_at = models.DateTimeField(null=True, blank=True)
  notification_url = models.CharField(max_length=500, null=True, blank=True)
  is_read = models.BooleanField(default=False)

  class Meta:
    ordering = ['-created_at']
    verbose_name = 'Notification'
    verbose_name_plural = 'Notifications'

  @staticmethod
  def auto_dismiss_notifications():
    Notification.objects.filter(
      status__in=[1, 2],
      created_at__lte=ExpressionWrapper(Now() - timedelta(days=15), output_field=DateTimeField())
    ).update(status=3)

class UndergraduateDegree(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class GraduateDegree(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class FacultyProfile(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='faculty_profile')
    academic_rank = models.CharField(max_length=255, null=True, blank=True)
    undergraduate_degrees = models.ManyToManyField(UndergraduateDegree, related_name='faculty_with_undergraduate', blank=True)
    graduate_degrees = models.ManyToManyField(GraduateDegree, related_name='faculty_with_graduate', blank=True)
    employment_status = models.IntegerField(choices=[(1, 'Permanent'), (2, 'Temporary'), (3, 'Casual'), (4, 'Contract of Service'), (5, 'Job Order'), (6, 'Coterminous'), (7, 'Contractual')], null=True, blank=True)
    institute = models.ForeignKey(Institutes, on_delete=models.CASCADE, null=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, null=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    core_time = models.CharField(max_length=255, null=True, blank=True)
    student_consultation_time = models.CharField(max_length=255, null=True, blank=True)
    date_hired = models.DateField(null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)


class AdminLoadRelease(models.Model):
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hour = models.FloatField()
    unit = models.FloatField()
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    group_id = models.ForeignKey(UserGroup, on_delete=models.CASCADE, blank=True, null=True)
    program_id = models.ForeignKey(Programs, on_delete=models.CASCADE, blank=True, null=True)


class REPLoadRelease(models.Model):
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hour = models.FloatField()
    unit = models.FloatField()
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    group_id = models.ForeignKey(UserGroup, on_delete=models.CASCADE, blank=True, null=True)
    program_id = models.ForeignKey(Programs, on_delete=models.CASCADE, blank=True, null=True)
    
    
class TeamTeach(models.Model):
    team_teach_id = models.AutoField(primary_key=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_leader')