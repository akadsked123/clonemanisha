# Generated by Django 5.0.8 on 2024-09-11 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0031_alter_usergroup_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='group_name',
            field=models.CharField(max_length=255),
        ),
    ]
