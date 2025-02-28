# Generated by Django 5.0.8 on 2024-11-15 13:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0020_alter_resultclassgroup_result_identification_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resultprogram',
            name='class_groups',
        ),
        migrations.AlterField(
            model_name='resultprogram',
            name='result_identification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification'),
        ),
        migrations.AddIndex(
            model_name='resultprogram',
            index=models.Index(fields=['result_identification'], name='result_prog_result__1d59ba_idx'),
        ),
    ]
