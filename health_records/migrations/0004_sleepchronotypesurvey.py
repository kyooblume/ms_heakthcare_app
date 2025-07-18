# Generated by Django 5.2.1 on 2025-06-28 01:56

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health_records', '0003_sleeprecord'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SleepChronotypeSurvey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday_bedtime', models.TimeField(blank=True, null=True, verbose_name='平日の就寝時刻')),
                ('weekday_wakeup_time', models.TimeField(blank=True, null=True, verbose_name='平日の起床時刻')),
                ('weekend_bedtime', models.TimeField(blank=True, null=True, verbose_name='休日の就寝時刻')),
                ('uses_alarm_on_weekend', models.BooleanField(default=True, verbose_name='休日にアラームを使うか')),
                ('weekend_natural_wakeup_time', models.TimeField(blank=True, help_text='もしアラームをかけなかった場合に起きるであろう時刻', null=True, verbose_name='休日に自然に起きる時刻')),
                ('sleep_quality', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='朝の目覚めの良さ (1-5)')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sleep_survey', to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name': '睡眠クロノタイプアンケート',
                'verbose_name_plural': '睡眠クロノタイプアンケート',
            },
        ),
    ]
