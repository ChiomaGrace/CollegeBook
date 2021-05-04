# Generated by Django 2.2.4 on 2021-05-01 21:56

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallApp', '0010_notification_hover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profilePic',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='submittedProfilePicImages'),
        ),
    ]