# Generated by Django 5.2.1 on 2025-06-22 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_userprofile_activity_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='height_cm',
            field=models.FloatField(blank=True, null=True, verbose_name='身長 (cm)'),
        ),
    ]
