# Generated by Django 5.0.8 on 2024-11-28 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0103_generatedschedule_unique_result_identification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initialschedulerdata',
            name='academic_year',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='initialschedulerdata',
            name='semester',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
