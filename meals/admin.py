from django.contrib import admin
from .models import MealLog, FoodMaster

#モデルを管理画面に登録
admin.site.register(MealLog)
admin.site.register(FoodMaster)