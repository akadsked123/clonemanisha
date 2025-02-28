# Generated by Django 5.0.8 on 2024-09-06 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0030_alter_programs_program_slug_and_more'),
        ('user', '0025_alter_groupmember_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmember',
            name='courses',
            field=models.ManyToManyField(blank=True, null=True, to='curriculum.courses'),
        ),
    ]
