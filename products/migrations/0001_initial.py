# Generated by Django 5.2.1 on 2025-06-28 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductNutrition',
            fields=[
                ('barcode', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='バーコード(JANコード)')),
                ('product_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='商品名')),
                ('calories', models.FloatField(blank=True, null=True, verbose_name='カロリー (kcal)')),
                ('protein', models.FloatField(blank=True, null=True, verbose_name='タンパク質 (g)')),
                ('fat', models.FloatField(blank=True, null=True, verbose_name='脂質 (g)')),
                ('carbohydrates', models.FloatField(blank=True, null=True, verbose_name='炭水化物 (g)')),
                ('image_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='商品画像URL')),
                ('source', models.CharField(default='openfoodfacts', max_length=50, verbose_name='情報源')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='最終更新日時')),
            ],
            options={
                'verbose_name': '商品栄養情報キャッシュ',
                'verbose_name_plural': '商品栄養情報キャッシュ',
            },
        ),
    ]
