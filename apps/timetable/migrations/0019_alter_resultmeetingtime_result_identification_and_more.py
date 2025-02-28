# Generated by Django 5.0.8 on 2024-11-15 10:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0018_alter_resultcourse_result_identification_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultmeetingtime',
            name='result_identification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification'),
        ),
        migrations.AddIndex(
            model_name='resultmeetingtime',
            index=models.Index(fields=['result_identification'], name='result_meet_result__f83e40_idx'),
        ),
    ]
