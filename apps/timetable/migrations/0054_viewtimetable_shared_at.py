# Generated by Django 5.0.8 on 2024-11-16 09:56

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0053_alter_initialschedulerdata_result_identification_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='viewtimetable',
            name='shared_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
