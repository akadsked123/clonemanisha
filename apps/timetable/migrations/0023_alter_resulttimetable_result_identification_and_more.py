# Generated by Django 5.0.8 on 2024-11-15 13:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0022_remove_resultprogram_courses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resulttimetable',
            name='result_identification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification'),
        ),
        migrations.AddIndex(
            model_name='resulttimetable',
            index=models.Index(fields=['result_identification'], name='result_time_result__78f77e_idx'),
        ),
    ]
