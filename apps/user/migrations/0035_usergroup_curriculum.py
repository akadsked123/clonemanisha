# Generated by Django 5.0.8 on 2024-09-12 12:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0033_alter_rooms_room_name'),
        ('user', '0034_alter_user_cover_image_alter_user_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='curriculum',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='curriculum.curriculumyear'),
            preserve_default=False,
        ),
    ]
