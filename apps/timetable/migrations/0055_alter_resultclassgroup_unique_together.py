# Generated by Django 5.0.8 on 2024-11-16 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0054_viewtimetable_shared_at'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='resultclassgroup',
            unique_together={('result_identification', 'class_group_id')},
        ),
    ]
