# Generated by Django 5.0.7 on 2024-08-24 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0021_alter_courses_course_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programs',
            name='program_code',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='programs',
            name='program_name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
