# Generated by Django 5.0.8 on 2024-11-15 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0037_remove_resultclassgroup_unique_class_group_id_result_identification_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resulttimetable',
            name='class_group',
        ),
        migrations.RemoveField(
            model_name='resulttimetable',
            name='classroom',
        ),
        migrations.RemoveField(
            model_name='resulttimetable',
            name='course',
        ),
        migrations.RemoveField(
            model_name='resulttimetable',
            name='instructor',
        ),
        migrations.RemoveField(
            model_name='resulttimetable',
            name='meeting_time',
        ),
    ]
