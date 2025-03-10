# Generated by Django 5.0.8 on 2024-11-17 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0038_auto_20241115_0204'),
        ('institutes', '0003_institutes_institutes_institu_2f9a7d_idx'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='courses',
            index=models.Index(fields=['course_id'], name='courses_course__bcfb55_idx'),
        ),
        migrations.AddIndex(
            model_name='curriculumyear',
            index=models.Index(fields=['curriculum_id'], name='curriculum__curricu_21d77b_idx'),
        ),
        migrations.AddIndex(
            model_name='programs',
            index=models.Index(fields=['program_id'], name='programs_program_61af52_idx'),
        ),
        migrations.AddIndex(
            model_name='rooms',
            index=models.Index(fields=['room_id'], name='rooms_room_id_331bb5_idx'),
        ),
    ]
