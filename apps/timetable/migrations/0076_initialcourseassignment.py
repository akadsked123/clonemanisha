# Generated by Django 5.0.8 on 2024-11-18 13:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0075_alter_resulttimetable_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InitialCourseAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_assign', models.BooleanField(default=False)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultcourse')),
                ('instructor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('result_identification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification')),
            ],
            options={
                'verbose_name': 'Course Assignment',
                'verbose_name_plural': 'Course Assignments',
                'db_table': 'course_assignment',
                'indexes': [models.Index(fields=['result_identification'], name='course_assi_result__4b6bdb_idx')],
            },
        ),
    ]
