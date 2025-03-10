# Generated by Django 5.0.8 on 2024-11-13 13:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('curriculum', '0033_alter_rooms_room_name'),
        ('institutes', '0002_alter_institutes_acronym_and_more'),
        ('timetable', '0002_auto_20241113_2111'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Periods',
            fields=[
                ('period_id', models.AutoField(primary_key=True, serialize=False)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'period',
                'verbose_name_plural': 'periods',
                'db_table': 'periods',
            },
        ),
        migrations.CreateModel(
            name='ResultIdentification',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Result Identification',
                'verbose_name_plural': 'Result Identifications',
                'db_table': 'result_identification',
            },
        ),
        migrations.CreateModel(
            name='TaskRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(max_length=255)),
                ('status', models.CharField(default='PENDING', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Weekday',
            fields=[
                ('day_id', models.AutoField(primary_key=True, serialize=False)),
                ('day_name', models.CharField(max_length=9, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GeneratedSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_identification', models.IntegerField()),
                ('json_file', models.FileField(upload_to='timetable_results/')),
                ('number_of_conflicts', models.IntegerField(blank=True, default=0, null=True)),
                ('academic_year', models.CharField(blank=True, max_length=100, null=True)),
                ('semester', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('total_generation_duration', models.IntegerField(blank=True, null=True)),
                ('created_by', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('institute', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='institutes.institutes')),
                ('program', models.ManyToManyField(blank=True, to='curriculum.programs')),
            ],
            options={
                'verbose_name': 'Generated Schedule',
                'verbose_name_plural': 'Generated Schedules',
                'db_table': 'generated_schedule',
            },
        ),
        migrations.CreateModel(
            name='InitialSchedulerData',
            fields=[
                ('scheduler_id', models.AutoField(primary_key=True, serialize=False)),
                ('academic_year', models.CharField(blank=True, max_length=10, null=True)),
                ('semester', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('progress', models.IntegerField(default=0)),
                ('remaining_time', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.IntegerField(choices=[(1, 'Inactive'), (2, 'Pending'), (3, 'Processing'), (4, 'Completed'), (5, 'Error'), (6, 'Cancelled')], default=2)),
                ('initial_data_json_file', models.FileField(blank=True, null=True, upload_to='scheduler_data/')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('generate_schedule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.generatedschedule')),
                ('institute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='institutes.institutes')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curriculum.programs')),
                ('task_record', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.taskrecord')),
            ],
            options={
                'verbose_name': 'Initial Scheduler Data',
                'verbose_name_plural': 'Initial Scheduler Data',
                'db_table': 'initial_scheduler_data',
            },
        ),
        migrations.AddField(
            model_name='generatedschedule',
            name='initial_scheduler_data',
            field=models.ManyToManyField(blank=True, to='timetable.initialschedulerdata'),
        ),
        migrations.CreateModel(
            name='ResultCourse',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('course_id', models.IntegerField(blank=True, null=True)),
                ('course_code', models.CharField(blank=True, max_length=255, null=True)),
                ('course_description', models.TextField(blank=True, null=True)),
                ('lecture_hours', models.IntegerField(blank=True, null=True)),
                ('laboratory_hours', models.IntegerField(blank=True, null=True)),
                ('credit_units', models.IntegerField(blank=True, null=True)),
                ('result_identification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification')),
            ],
            options={
                'verbose_name': 'Result Course',
                'verbose_name_plural': 'Result Courses',
                'db_table': 'result_course',
            },
        ),
        migrations.CreateModel(
            name='ResultClassroom',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('room_id', models.IntegerField(blank=True, null=True)),
                ('room_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_lab', models.BooleanField(blank=True, null=True)),
                ('result_identification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification')),
            ],
            options={
                'verbose_name': 'Result Classroom',
                'verbose_name_plural': 'Result Classrooms',
                'db_table': 'result_classroom',
            },
        ),
        migrations.CreateModel(
            name='ResultClassGroup',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('class_group_id', models.IntegerField(blank=True, null=True)),
                ('class_group_name', models.CharField(blank=True, max_length=255, null=True)),
                ('year_level', models.IntegerField(blank=True, null=True)),
                ('schedule_courses', models.ManyToManyField(blank=True, related_name='class_groups', to='timetable.resultcourse')),
                ('result_identification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification')),
            ],
            options={
                'verbose_name': 'Result Class Group',
                'verbose_name_plural': 'Result Class Groups',
                'db_table': 'result_class_group',
            },
        ),
        migrations.CreateModel(
            name='ResultMeetingTime',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('meeting_id', models.IntegerField(blank=True, null=True)),
                ('meeting_time', models.CharField(blank=True, max_length=255, null=True)),
                ('credit_hours', models.IntegerField(blank=True, null=True)),
                ('conflicts', models.ManyToManyField(blank=True, related_name='conflicting_times', to='timetable.resultmeetingtime')),
                ('result_identification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification')),
            ],
            options={
                'verbose_name': 'Result Meeting Time',
                'verbose_name_plural': 'Result Meeting Times',
                'db_table': 'result_meeting_time',
            },
        ),
        migrations.CreateModel(
            name='ResultInstructor',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('instructor_id', models.IntegerField(blank=True, null=True)),
                ('instructor_name', models.CharField(blank=True, max_length=255, null=True)),
                ('courses', models.ManyToManyField(blank=True, related_name='instructors', to='timetable.resultcourse')),
                ('result_identification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification')),
                ('availability', models.ManyToManyField(blank=True, related_name='available_instructors', to='timetable.resultmeetingtime')),
            ],
            options={
                'verbose_name': 'Result Instructor',
                'verbose_name_plural': 'Result Instructors',
                'db_table': 'result_instructor',
            },
        ),
        migrations.CreateModel(
            name='ResultProgram',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('program_id', models.IntegerField(blank=True, null=True)),
                ('program_name', models.CharField(blank=True, max_length=255, null=True)),
                ('program_code', models.CharField(blank=True, max_length=255, null=True)),
                ('class_groups', models.ManyToManyField(blank=True, related_name='programs', to='timetable.resultclassgroup')),
                ('courses', models.ManyToManyField(blank=True, related_name='programs', to='timetable.resultcourse')),
                ('result_identification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification')),
            ],
            options={
                'verbose_name': 'Result Program',
                'verbose_name_plural': 'Result Programs',
                'db_table': 'result_program',
            },
        ),
        migrations.CreateModel(
            name='ResultTimetable',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('class_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultclassgroup')),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultclassroom')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultcourse')),
                ('instructor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultinstructor')),
                ('meeting_time', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultmeetingtime')),
                ('result_identification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification')),
            ],
            options={
                'verbose_name': 'Result Timetable',
                'verbose_name_plural': 'Result Timetables',
                'db_table': 'result_timetable',
            },
        ),
        migrations.CreateModel(
            name='ViewTimetable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share_to_instructor', models.BooleanField(default=False)),
                ('generated_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.generatedschedule')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'View Timetable',
                'verbose_name_plural': 'View Timetables',
                'db_table': 'view_timetable',
            },
        ),
        migrations.AddConstraint(
            model_name='initialschedulerdata',
            constraint=models.UniqueConstraint(condition=models.Q(('status__in', [2, 3])), fields=('institute', 'program', 'semester'), name='unique_active_processing_per_institute_program_semester'),
        ),
        migrations.AlterUniqueTogether(
            name='viewtimetable',
            unique_together={('generated_schedule', 'share_to_instructor', 'user')},
        ),
    ]
