# Generated by Django 5.0.7 on 2024-08-18 12:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0017_remove_courses_is_major_course'),
        ('institutes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculumyear',
            name='institute',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='institutes.institutes'),
            preserve_default=False,
        ),
    ]
