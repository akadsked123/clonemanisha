# Generated by Django 5.0.8 on 2024-09-11 13:36

import apps.user.common.account_compress_image
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0033_alter_rooms_room_name'),
        ('institutes', '0002_alter_institutes_acronym_and_more'),
        ('user', '0029_alter_user_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='date_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='institute',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='institutes.institutes'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='program',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='curriculum.programs'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=apps.user.common.account_compress_image.ProfileImageField(upload_to='profile_image/'),
        ),
    ]
