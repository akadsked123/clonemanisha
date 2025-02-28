from django.db import models
from django.utils.text import slugify

class Institutes(models.Model):
    institute_id = models.AutoField(primary_key=True)
    institute_name = models.CharField(max_length=100, unique=True, null=False)
    acronym = models.CharField(max_length=50, unique=True, null=False)
    institute_slug = models.SlugField(max_length=255, unique=True, null=False)

    class Meta:
        db_table = "institutes"
        verbose_name = 'Institute'
        verbose_name_plural = 'Institutes'
        indexes = [
            models.Index(fields=['institute_id']),
        ]

    def __str__(self):
        return self.institute_name
    
    def save(self, *args, **kwargs):
            if not self.institute_slug:
                self.institute_slug = slugify(self.institute_name)
            super().save(*args, **kwargs)