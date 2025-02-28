# Generated by Django 5.0.7 on 2024-08-24 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0024_alter_programs_program_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programs',
            name='program_slug',
            field=models.SlugField(default=1, max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
