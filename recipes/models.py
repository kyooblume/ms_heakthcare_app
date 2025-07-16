# recipes/models.py

from django.db import models

class Recipe(models.Model):
    """
    一つのレシピ（献立）を表すモデル。
    """
    title = models.CharField(max_length=200, verbose_name='料理名')
    description = models.TextField(blank=True, verbose_name='料理の説明')
    instructions = models.TextField(verbose_name='作り方')
    image_url = models.URLField(blank=True, null=True, verbose_name='料理の画像URL')

    # このレシピから摂取できるおおよその栄養素
    total_calories = models.FloatField(default=0, verbose_name='総カロリー (kcal)')
    total_protein = models.FloatField(default=0, verbose_name='総タンパク質 (g)')
    total_fat = models.FloatField(default=0, verbose_name='総脂質 (g)')
    total_carbohydrates = models.FloatField(default=0, verbose_name='総炭水化物 (g)')

    def __str__(self):
        return self.title

class Ingredient(models.Model):
    """
    レシピに含まれる材料を表すモデル。
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=200, verbose_name='材料名')
    quantity = models.CharField(max_length=100, verbose_name='分量（例: 1個, 100g）')

    def __str__(self):
        return f"{self.name} for {self.recipe.title}"