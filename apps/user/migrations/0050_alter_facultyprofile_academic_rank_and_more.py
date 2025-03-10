# Generated by Django 5.0.8 on 2025-01-08 11:02

import apps.user.common.account_compress_image
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0040_courses_is_major_course'),
        ('institutes', '0003_institutes_institutes_institu_2f9a7d_idx'),
        ('user', '0049_alter_user_cover_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facultyprofile',
            name='academic_rank',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='core_time',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='date_created',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='date_hired',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='department',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='designation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='employment_status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='graduate_degree',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='institute',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='institutes.institutes'),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='curriculum.programs'),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='undergraduate_degree',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='facultyprofile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faculty_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='cover_image',
            field=apps.user.common.account_compress_image.CoverImageField(default='cover_image/1610112024235135.jpg', upload_to='cover_image/'),
        ),
    ]
