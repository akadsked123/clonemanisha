# Generated by Django 5.0.8 on 2025-01-09 09:22

import apps.user.common.account_compress_image
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0053_alter_facultyprofile_employment_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cover_image',
            field=apps.user.common.account_compress_image.CoverImageField(default='cover_image/107012025225252.jpg', upload_to='cover_image/'),
        ),
    ]
