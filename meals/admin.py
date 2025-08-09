from django.contrib import admin
from .models import MealLog, FoodMaster

#モデルを管理画面に登録
admin.site.register(MealLog)
admin.site.register(FoodMaster)

from .models import Meal, MealItem, FoodMaster

# ↓↓↓ 新しいモデルを管理画面に登録します
admin.site.register(Meal)
admin.site.register(MealItem)
admin.site.register(FoodMaster)
