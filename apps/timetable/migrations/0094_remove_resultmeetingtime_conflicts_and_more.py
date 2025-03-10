# Generated by Django 5.0.8 on 2024-11-20 14:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0093_resultmeetingtime_end_time_resultmeetingtime_f2f_day_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resultmeetingtime',
            name='conflicts',
        ),
        migrations.RemoveField(
            model_name='resultmeetingtime',
            name='credit_hours',
        ),
        migrations.RemoveField(
            model_name='resultmeetingtime',
            name='f2f_day',
        ),
        migrations.RemoveField(
            model_name='resultmeetingtime',
            name='flexible_day',
        ),
        migrations.RemoveField(
            model_name='resultmeetingtime',
            name='meeting_time',
        ),
        migrations.AlterUniqueTogether(
            name='resulttimetable',
            unique_together={('result_id', 'result_identification', 'instructor', 'class_group_id', 'course_id')},
        ),
        migrations.AddField(
            model_name='resultmeetingtime',
            name='is_online_meeting',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='initialcourseassignment',
            name='course_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultcourse'),
        ),
        migrations.AlterField(
            model_name='initialcourseassignment',
            name='instructor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='initialcourseassignment',
            name='is_assign',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='initialschedulerdata',
            name='result_identification',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='resultclassgroup',
            name='class_group_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='resultclassgroup',
            name='class_group_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='resultclassroom',
            name='room_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='resultclassroom',
            name='room_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='resultinstructor',
            name='instructor_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='resultprogram',
            name='program_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='resultprogram',
            name='program_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='resultprogram',
            name='program_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.RemoveField(
            model_name='resulttimetable',
            name='classroom_id',
        ),
        migrations.RemoveField(
            model_name='resulttimetable',
            name='meeting_time_id',
        ),
        migrations.CreateModel(
            name='ResultTimetableDetail',
            fields=[
                ('result_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('room_id', models.IntegerField(blank=True, null=True)),
                ('meeting_id', models.IntegerField(blank=True, null=True)),
                ('result_identification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification')),
                ('result_timetable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='timetable.resulttimetable')),
            ],
            options={
                'verbose_name': 'Result Timetable Detail',
                'verbose_name_plural': 'Result Timetable Details',
                'db_table': 'result_timetable_detail',
                'indexes': [models.Index(fields=['result_identification'], name='result_time_result__83ffce_idx')],
                'unique_together': {('result_id', 'result_identification', 'room_id', 'meeting_id')},
            },
        ),
    ]
