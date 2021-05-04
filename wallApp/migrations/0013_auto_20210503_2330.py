# Generated by Django 2.2.4 on 2021-05-03 23:30

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallApp', '0012_auto_20210501_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profilePic',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True),
        ),
    ]
