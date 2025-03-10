# Generated by Django 5.0.8 on 2024-11-18 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0076_initialcourseassignment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='initialcourseassignment',
            options={'verbose_name': 'Initial Course Assignment', 'verbose_name_plural': 'Initial Course Assignments'},
        ),
        migrations.RenameIndex(
            model_name='initialcourseassignment',
            new_name='initial_cou_result__64d28f_idx',
            old_name='course_assi_result__4b6bdb_idx',
        ),
        migrations.AlterModelTable(
            name='initialcourseassignment',
            table='initial_course_assignment',
        ),
    ]
