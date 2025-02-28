# Generated by Django 5.0.8 on 2025-01-07 17:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp_email', '0006_add_timestamps'),
        ('user', '0044_alter_facultyprofile_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangePasswordOTP',
            fields=[
                ('emaildevice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='otp_email.emaildevice')),
            ],
            options={
                'abstract': False,
            },
            bases=('otp_email.emaildevice',),
        ),
    ]
