# Generated by Django 5.0.8 on 2024-11-26 06:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0039_courses_courses_course__bcfb55_idx_and_more'),
        ('institutes', '0003_institutes_institutes_institu_2f9a7d_idx'),
        ('timetable', '0102_remove_generatedschedule_early_mutation_rate'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='generatedschedule',
            constraint=models.UniqueConstraint(fields=('result_identification',), name='unique_result_identification'),
        ),
    ]
