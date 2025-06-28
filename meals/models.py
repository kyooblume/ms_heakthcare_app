# meals/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class Meal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='ユーザー')
    MEAL_TYPE_CHOICES = [
        ('breakfast', '朝食'),
        ('lunch', '昼食'),
        ('dinner', '夕食'),
        ('snack', '間食'),
    ]
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES, verbose_name='食事タイプ')
    notes = models.TextField(blank=True, verbose_name='メモ')
    # Django 5.0以降では default=timezone.now の代わりに、
    # auto_now_add=True を使うのが一般的ですが、ここでは既存の構造を尊重します。
    recorded_at = models.DateTimeField(default=timezone.now, verbose_name='食事日時')

    def __str__(self):
        return f"{self.user.username} - {self.get_meal_type_display()} at {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

# meals/models.py の FoodMaster モデル
class FoodMaster(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='食品名')
    
    # --- ご提示の列名に合わせたフィールド ---
    calories_per_100g = models.PositiveIntegerField(verbose_name='エネルギー', default=0)
    water_g = models.FloatField(verbose_name='水分', default=0)
    protein_per_100g = models.FloatField(verbose_name='たんぱく質', default=0)
    fat_per_100g = models.FloatField(verbose_name='脂質', default=0)
    carbohydrate_per_100g = models.FloatField(verbose_name='炭水化物', default=0)
    sodium_mg = models.PositiveIntegerField(verbose_name='ナトリウム', default=0)
    potassium_mg = models.PositiveIntegerField(verbose_name='カリウム', default=0)
    calcium_mg = models.PositiveIntegerField(verbose_name='カルシウム', default=0)
    magnesium_mg = models.PositiveIntegerField(verbose_name='マグネシウム', default=0)
    phosphorus_mg = models.PositiveIntegerField(verbose_name='リン', default=0)
    iron_mg = models.FloatField(verbose_name='鉄', default=0)
    zinc_mg = models.FloatField(verbose_name='亜鉛', default=0)
    copper_mg = models.FloatField(verbose_name='銅', default=0)
    manganese_mg = models.FloatField(verbose_name='マンガン', default=0)
    iodine_mcg = models.PositiveIntegerField(verbose_name='ヨウ素', default=0)
    selenium_mcg = models.PositiveIntegerField(verbose_name='セレン', default=0)
    chromium_mcg = models.PositiveIntegerField(verbose_name='クロム', default=0)
    molybdenum_mcg = models.PositiveIntegerField(verbose_name='モリブデン', default=0)
    vitamin_a_mcg = models.PositiveIntegerField(verbose_name='ビタミンA', default=0)
    vitamin_d_mcg = models.FloatField(verbose_name='ビタミンD', default=0)
    vitamin_e_mg = models.FloatField(verbose_name='ビタミンE', default=0)
    vitamin_k_mcg = models.PositiveIntegerField(verbose_name='ビタミンK', default=0)
    vitamin_b1_mg = models.FloatField(verbose_name='ビタミンB1', default=0)
    vitamin_b2_mg = models.FloatField(verbose_name='ビタミンB2', default=0)
    niacin_mg = models.FloatField(verbose_name='ナイアシン当量', default=0)
    vitamin_b6_mg = models.FloatField(verbose_name='ビタミンB6', default=0)
    vitamin_b12_mcg = models.FloatField(verbose_name='ビタミンB12', default=0)
    folate_mcg = models.PositiveIntegerField(verbose_name='葉酸', default=0)
    pantothenic_acid_mg = models.FloatField(verbose_name='パントテン酸', default=0)
    biotin_mcg = models.FloatField(verbose_name='ビオチン', default=0)
    vitamin_c_mg = models.FloatField(verbose_name='ビタミンC', default=0)
    alcohol_g = models.FloatField(verbose_name='アルコール', default=0)
    salt_equivalent_per_100g = models.FloatField(verbose_name='食塩相当量', default=0)

    def __str__(self):
        return self.name
# 食事記録の大枠モデル
class MealLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='ユーザー')
    MEAL_TYPE_CHOICES = [
        ('breakfast', '朝食'),
        ('lunch', '昼食'),
        ('dinner', '夕食'),
        ('snack', '間食'),
    ]
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES, verbose_name='食事タイプ')
    notes = models.TextField(blank=True, verbose_name='メモ')
    eaten_at = models.DateTimeField(default=timezone.now, verbose_name='食事日時')

    def __str__(self):
        return f"{self.user.username} - {self.get_meal_type_display()} at {self.eaten_at.strftime('%Y-%m-%d %H:%M')}"

# 食事の具体的な内容モデル
class MealComponent(models.Model):
    meal_log = models.ForeignKey(MealLog, on_delete=models.CASCADE, related_name='components', verbose_name='食事記録')
    food = models.ForeignKey(FoodMaster, on_delete=models.PROTECT, verbose_name='食品')
    quantity = models.FloatField(verbose_name='量 (g)')

    def __str__(self):
        return f"{self.food.name} - {self.quantity}g"
    

class MealItem(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='items', verbose_name='食事')
    food_name = models.CharField(max_length=200, verbose_name='食品名')
    
    # --- ★ここから修正・追加 ---
    # 栄養素のフィールドは、nullを許可しておく
    calories = models.FloatField(null=True, blank=True, verbose_name='カロリー (kcal)')
    protein = models.FloatField(null=True, blank=True, verbose_name='タンパク質 (g)')
    fat = models.FloatField(null=True, blank=True, verbose_name='脂質 (g)')
    carbohydrates = models.FloatField(null=True, blank=True, verbose_name='炭水化物 (g)')
    
    # 食べた量を記録するフィールドを追加
    quantity = models.FloatField(default=1.0, verbose_name='量')
    unit = models.CharField(max_length=50, default='serving', verbose_name='単位 (例: g, ml, 個)')
    # --- ★ここまで修正・追加 ---

    def __str__(self):
        return f"{self.food_name} in {self.meal}"