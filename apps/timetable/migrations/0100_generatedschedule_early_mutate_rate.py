# Generated by Django 5.0.8 on 2024-11-25 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0099_remove_generatedschedule_crossover_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatedschedule',
            name='early_mutate_rate',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
