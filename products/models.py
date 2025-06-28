# products/models.py

from django.db import models

class ProductNutrition(models.Model):
    barcode = models.CharField(max_length=20, primary_key=True, verbose_name='バーコード(JANコード)')
    product_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='商品名')
    
    # 100gあたりの栄養素
    calories = models.FloatField(null=True, blank=True, verbose_name='カロリー (kcal)')
    protein = models.FloatField(null=True, blank=True, verbose_name='タンパク質 (g)')
    fat = models.FloatField(null=True, blank=True, verbose_name='脂質 (g)')
    carbohydrates = models.FloatField(null=True, blank=True, verbose_name='炭水化物 (g)')
    
    image_url = models.URLField(max_length=255, null=True, blank=True, verbose_name='商品画像URL')
    source = models.CharField(max_length=50, default='openfoodfacts', verbose_name='情報源')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最終更新日時')

    def __str__(self):
        return f"{self.product_name} ({self.barcode})"

    class Meta:
        verbose_name = '商品栄養情報キャッシュ'
        verbose_name_plural = '商品栄養情報キャッシュ'