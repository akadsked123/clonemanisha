# Generated by Django 5.0.8 on 2025-02-05 13:25

import apps.user.common.account_compress_image
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0057_alter_user_cover_image_alter_user_position_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminloadrelease',
            name='group_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.usergroup'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reploadrelease',
            name='group_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.usergroup'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='cover_image',
            field=apps.user.common.account_compress_image.CoverImageField(default='cover_image/108012025013034.jpg', upload_to='cover_image/'),
        ),
    ]
