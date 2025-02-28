# Generated by Django 5.0.8 on 2025-01-07 09:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0043_facultyprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facultyprofile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
