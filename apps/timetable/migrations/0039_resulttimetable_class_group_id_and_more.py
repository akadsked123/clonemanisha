# Generated by Django 5.0.8 on 2024-11-15 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0038_remove_resulttimetable_class_group_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='resulttimetable',
            name='class_group_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resulttimetable',
            name='classroom_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resulttimetable',
            name='course_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resulttimetable',
            name='instructor_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resulttimetable',
            name='meeting_time_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
