# Generated by Django 5.0.7 on 2024-08-19 14:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0018_curriculumyear_institute'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='programs',
            name='curriculum',
        ),
        migrations.AddField(
            model_name='curriculumyear',
            name='program',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='curriculum.programs'),
            preserve_default=False,
        ),
    ]
