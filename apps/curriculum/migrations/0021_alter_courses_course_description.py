# Generated by Django 5.0.7 on 2024-08-24 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0020_alter_courses_course_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courses',
            name='course_description',
            field=models.TextField(max_length=100),
        ),
    ]
