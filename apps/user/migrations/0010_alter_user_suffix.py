# Generated by Django 4.2.11 on 2024-07-27 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_user_phone_number_alter_user_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='suffix',
            field=models.CharField(blank=True, default='', max_length=10, null=True),
        ),
    ]
