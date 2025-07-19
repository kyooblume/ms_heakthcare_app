

# Register your models here.
# recipes/admin.py

from django.contrib import admin
from .models import Recipe, Ingredient

# レシピと材料モデルを登録
admin.site.register(Recipe)
admin.site.register(Ingredient)