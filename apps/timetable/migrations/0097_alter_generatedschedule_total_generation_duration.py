# Generated by Django 5.0.8 on 2024-11-25 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0096_rename_id_initialcourseassignment_assignment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generatedschedule',
            name='total_generation_duration',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
