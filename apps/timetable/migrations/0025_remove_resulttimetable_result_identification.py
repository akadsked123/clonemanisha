# Generated by Django 5.0.8 on 2024-11-15 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0024_remove_resulttimetable_result_time_result__78f77e_idx'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resulttimetable',
            name='result_identification',
        ),
    ]
