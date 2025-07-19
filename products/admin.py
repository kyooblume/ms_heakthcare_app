

# Register your models here.
# products/admin.py

from django.contrib import admin
from .models import ProductNutrition

# 商品キャッシュモデルを登録
admin.site.register(ProductNutrition)