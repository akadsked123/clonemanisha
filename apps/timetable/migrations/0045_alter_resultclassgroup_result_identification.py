# Generated by Django 5.0.8 on 2024-11-16 09:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0044_alter_resultprogram_program_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultclassgroup',
            name='result_identification',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='timetable.resultidentification'),
            preserve_default=False,
        ),
    ]
