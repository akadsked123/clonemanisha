# Generated by Django 4.2.11 on 2024-07-25 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_user_program'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='designation',
        ),
        migrations.AlterField(
            model_name='user',
            name='program',
            field=models.IntegerField(blank=True, choices=[(1, 'Bachelor of Science in Information Technology'), (2, 'Bachelor of Science in Information Systems')], null=True),
        ),
    ]
