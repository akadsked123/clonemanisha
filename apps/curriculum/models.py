from django.db import models
from django.utils.text import slugify
from apps.institutes.models import Institutes
from django.db.models import UniqueConstraint

class Programs(models.Model):
    program_id = models.AutoField(primary_key=True)
    program_code = models.CharField(max_length=100, unique=True, null=False)
    program_name = models.CharField(max_length=255, unique=True, null=False)
    program_slug = models.SlugField(max_length=255, unique=True, null=False)
    institute = models.ForeignKey(Institutes, on_delete=models.CASCADE, null=False)

    class Meta:  
        db_table = "programs"
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
        indexes = [
            models.Index(fields=['program_id']),
        ]
    
    def __str__(self):
        return self.program_name
    
    def save(self, *args, **kwargs):
        if not self.program_slug:
            self.program_slug = slugify(self.program_name)
        super().save(*args, **kwargs)
        
class CurriculumYear(models.Model):
    curriculum_id = models.AutoField(primary_key=True)
    curriculum_year = models.CharField(max_length=255)
    institute = models.ForeignKey(Institutes, on_delete=models.CASCADE)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)

    class Meta:
        db_table = "curriculum_year"
        verbose_name = 'Curriculum Year'
        verbose_name_plural = 'Curriculum Year'
        constraints = [
            UniqueConstraint(fields=['curriculum_year', 'institute', 'program'], name='unique_curriculum_year_institute_program')
        ]
        indexes = [
            models.Index(fields=['curriculum_id']),
        ]
    
    def save(self, *args, **kwargs):
        # Check if a CurriculumYear with the same name, institute, and program already exists
        original_name = self.curriculum_year
        if CurriculumYear.objects.filter(
            curriculum_year=self.curriculum_year,
            institute=self.institute,
            program=self.program
        ).exists():
            counter = 1  # Start numbering from 1
            while CurriculumYear.objects.filter(
                curriculum_year=f"{original_name} ({counter})",
                institute=self.institute,
                program=self.program
            ).exists():
                counter += 1
            self.curriculum_year = f"{original_name} ({counter})"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.curriculum_year} - {self.program} - {self.institute}"
    

class Rooms(models.Model):
    room_id = models.AutoField(primary_key=True)
    room_name = models.CharField(max_length=100, unique=True)
    is_lab = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now=True)
    building = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:  
        db_table = "rooms"
        verbose_name = 'Classroom'
        verbose_name_plural = 'Classrooms'
        indexes = [
            models.Index(fields=['room_id']),
        ]
    
    def __str__(self):
        return self.room_name

class Courses(models.Model):
    course_id = models.AutoField(primary_key=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, max_length=50)
    curriculum = models.ForeignKey(CurriculumYear, on_delete=models.CASCADE)
    course_code = models.CharField(max_length=10)
    course_description = models.TextField(max_length=100)
    lecture = models.IntegerField(default=0) 
    laboratory = models.IntegerField(default=0)
    credit_units = models.IntegerField(default=0)
    semester = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_lab = models.BooleanField(default=False)
    year_level = models.IntegerField(default=1)
    is_major_course = models.BooleanField(default=False)

    class Meta:  
        db_table = "courses"
        verbose_name = 'course'
        verbose_name_plural = 'courses'
        indexes = [
            models.Index(fields=['course_id']),
        ]
    
    def __str__(self):
        return self.course_code