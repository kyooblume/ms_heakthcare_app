# Generated by Django 5.2.1 on 2025-07-19 01:54

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='食品名')),
                ('calories_per_100g', models.PositiveIntegerField(default=0, verbose_name='エネルギー')),
                ('water_g', models.FloatField(default=0, verbose_name='水分')),
                ('protein_per_100g', models.FloatField(default=0, verbose_name='たんぱく質')),
                ('fat_per_100g', models.FloatField(default=0, verbose_name='脂質')),
                ('carbohydrate_per_100g', models.FloatField(default=0, verbose_name='炭水化物')),
                ('sodium_mg', models.PositiveIntegerField(default=0, verbose_name='ナトリウム')),
                ('potassium_mg', models.PositiveIntegerField(default=0, verbose_name='カリウム')),
                ('calcium_mg', models.PositiveIntegerField(default=0, verbose_name='カルシウム')),
                ('magnesium_mg', models.PositiveIntegerField(default=0, verbose_name='マグネシウム')),
                ('phosphorus_mg', models.PositiveIntegerField(default=0, verbose_name='リン')),
                ('iron_mg', models.FloatField(default=0, verbose_name='鉄')),
                ('zinc_mg', models.FloatField(default=0, verbose_name='亜鉛')),
                ('copper_mg', models.FloatField(default=0, verbose_name='銅')),
                ('manganese_mg', models.FloatField(default=0, verbose_name='マンガン')),
                ('iodine_mcg', models.PositiveIntegerField(default=0, verbose_name='ヨウ素')),
                ('selenium_mcg', models.PositiveIntegerField(default=0, verbose_name='セレン')),
                ('chromium_mcg', models.PositiveIntegerField(default=0, verbose_name='クロム')),
                ('molybdenum_mcg', models.PositiveIntegerField(default=0, verbose_name='モリブデン')),
                ('vitamin_a_mcg', models.PositiveIntegerField(default=0, verbose_name='ビタミンA')),
                ('vitamin_d_mcg', models.FloatField(default=0, verbose_name='ビタミンD')),
                ('vitamin_e_mg', models.FloatField(default=0, verbose_name='ビタミンE')),
                ('vitamin_k_mcg', models.PositiveIntegerField(default=0, verbose_name='ビタミンK')),
                ('vitamin_b1_mg', models.FloatField(default=0, verbose_name='ビタミンB1')),
                ('vitamin_b2_mg', models.FloatField(default=0, verbose_name='ビタミンB2')),
                ('niacin_mg', models.FloatField(default=0, verbose_name='ナイアシン当量')),
                ('vitamin_b6_mg', models.FloatField(default=0, verbose_name='ビタミンB6')),
                ('vitamin_b12_mcg', models.FloatField(default=0, verbose_name='ビタミンB12')),
                ('folate_mcg', models.PositiveIntegerField(default=0, verbose_name='葉酸')),
                ('pantothenic_acid_mg', models.FloatField(default=0, verbose_name='パントテン酸')),
                ('biotin_mcg', models.FloatField(default=0, verbose_name='ビオチン')),
                ('vitamin_c_mg', models.FloatField(default=0, verbose_name='ビタミンC')),
                ('alcohol_g', models.FloatField(default=0, verbose_name='アルコール')),
                ('salt_equivalent_per_100g', models.FloatField(default=0, verbose_name='食塩相当量')),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_type', models.CharField(choices=[('breakfast', '朝食'), ('lunch', '昼食'), ('dinner', '夕食'), ('snack', '間食')], max_length=10, verbose_name='食事タイプ')),
                ('notes', models.TextField(blank=True, verbose_name='メモ')),
                ('recorded_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='食事日時')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
        ),
        migrations.CreateModel(
            name='MealItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_name', models.CharField(max_length=200, verbose_name='食品名')),
                ('calories', models.FloatField(blank=True, null=True, verbose_name='カロリー (kcal)')),
                ('protein', models.FloatField(blank=True, null=True, verbose_name='タンパク質 (g)')),
                ('fat', models.FloatField(blank=True, null=True, verbose_name='脂質 (g)')),
                ('carbohydrates', models.FloatField(blank=True, null=True, verbose_name='炭水化物 (g)')),
                ('quantity', models.FloatField(default=1.0, verbose_name='量')),
                ('unit', models.CharField(default='serving', max_length=50, verbose_name='単位 (例: g, ml, 個)')),
                ('meal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='meals.meal', verbose_name='食事')),
            ],
        ),
        migrations.CreateModel(
            name='MealLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_type', models.CharField(choices=[('breakfast', '朝食'), ('lunch', '昼食'), ('dinner', '夕食'), ('snack', '間食')], max_length=10, verbose_name='食事タイプ')),
                ('notes', models.TextField(blank=True, verbose_name='メモ')),
                ('eaten_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='食事日時')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
        ),
        migrations.CreateModel(
            name='MealComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(verbose_name='量 (g)')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='meals.foodmaster', verbose_name='食品')),
                ('meal_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='meals.meallog', verbose_name='食事記録')),
            ],
        ),
    ]
