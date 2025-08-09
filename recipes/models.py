# recipes/models.py - 拡張版

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Recipe(models.Model):
    """
    栄養最適化に対応した拡張レシピモデル
    """
    # 基本情報
    title = models.CharField(max_length=200, verbose_name='料理名')
    description = models.TextField(blank=True, verbose_name='料理の説明')
    instructions = models.TextField(verbose_name='作り方')
    image_url = models.URLField(blank=True, null=True, verbose_name='料理の画像URL')
    
    # 調理情報
    prep_time = models.PositiveIntegerField(default=0, verbose_name='準備時間（分）')
    cook_time = models.PositiveIntegerField(default=0, verbose_name='調理時間（分）')
    servings = models.PositiveIntegerField(default=1, verbose_name='何人分')
    difficulty = models.CharField(
        max_length=10,
        choices=[('easy', '簡単'), ('medium', '普通'), ('hard', '難しい')],
        default='medium',
        verbose_name='難易度'
    )
    
    # 基本栄養素（100g当たりまたは1人分）
    total_calories = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='総カロリー (kcal)'
    )
    total_protein = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='総タンパク質 (g)'
    )
    total_fat = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='総脂質 (g)'
    )
    total_carbohydrates = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='総炭水化物 (g)'
    )
    
    # 詳細栄養素（線形計画法での制約に使用）
    total_fiber = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='食物繊維 (g)',
        help_text='消化器官の健康に重要'
    )
    total_sugar = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='糖質 (g)',
        help_text='炭水化物の内、糖質の量'
    )
    total_sodium = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='ナトリウム (mg)',
        help_text='塩分制限に使用'
    )
    
    # ビタミン・ミネラル
    total_calcium = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='カルシウム (mg)'
    )
    total_iron = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='鉄分 (mg)'
    )
    total_vitamin_c = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='ビタミンC (mg)'
    )
    total_vitamin_d = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='ビタミンD (μg)'
    )
    
    # コスト・利便性
    estimated_cost = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='推定コスト (円)',
        help_text='1人分の推定コスト'
    )
    
    # カテゴリ・タグ
    meal_type = models.CharField(
        max_length=20,
        choices=[
            ('breakfast', '朝食'),
            ('lunch', '昼食'),
            ('dinner', '夕食'),
            ('snack', '間食'),
            ('any', '任意')
        ],
        default='any',
        verbose_name='食事タイプ'
    )
    
    cuisine_type = models.CharField(
        max_length=30,
        choices=[
            ('japanese', '和食'),
            ('western', '洋食'),
            ('chinese', '中華'),
            ('korean', '韓国料理'),
            ('italian', 'イタリアン'),
            ('other', 'その他')
        ],
        default='japanese',
        verbose_name='料理ジャンル'
    )
    
    # 食事制限対応
    is_vegetarian = models.BooleanField(default=False, verbose_name='ベジタリアン対応')
    is_vegan = models.BooleanField(default=False, verbose_name='ビーガン対応')
    is_gluten_free = models.BooleanField(default=False, verbose_name='グルテンフリー')
    is_dairy_free = models.BooleanField(default=False, verbose_name='乳製品不使用')
    
    # 最適化用メタデータ
    nutritional_density_score = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='栄養密度スコア',
        help_text='カロリー当たりの栄養価（自動計算）'
    )
    
    optimization_priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='最適化優先度',
        help_text='線形計画法での優先度（1=低, 10=高）'
    )
    
    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    is_active = models.BooleanField(default=True, verbose_name='有効')
    
    class Meta:
        ordering = ['-optimization_priority', 'title']
        indexes = [
            models.Index(fields=['meal_type', 'is_active']),
            models.Index(fields=['total_protein', 'total_calories']),
            models.Index(fields=['optimization_priority']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.total_calories}kcal)"
    
    def save(self, *args, **kwargs):
        """保存時に栄養密度スコアを自動計算"""
        if self.total_calories > 0:
            # 栄養密度 = (タンパク質*4 + 食物繊維*2 + ビタミン・ミネラル) / カロリー * 100
            nutrition_score = (
                self.total_protein * 4 +  # タンパク質重視
                self.total_fiber * 2 +    # 食物繊維
                (self.total_calcium / 100) +  # カルシウム
                (self.total_iron * 10) +      # 鉄分
                (self.total_vitamin_c / 10)   # ビタミンC
            )
            self.nutritional_density_score = min(100, (nutrition_score / self.total_calories) * 100)
        else:
            self.nutritional_density_score = 0
        
        super().save(*args, **kwargs)
    
    @property
    def total_prep_time(self):
        """総調理時間"""
        return self.prep_time + self.cook_time
    
    @property
    def nutrition_vector(self):
        """線形計画法用の栄養素ベクトル"""
        return [
            self.total_protein,
            self.total_fat,
            self.total_carbohydrates,
            self.total_calories,
            self.total_fiber,
            self.total_sodium,
            self.total_sugar,
            self.total_calcium,
            self.total_iron,
            self.total_vitamin_c
        ]
    
    @property
    def dietary_restrictions(self):
        """食事制限リスト"""
        restrictions = []
        if self.is_vegetarian:
            restrictions.append('vegetarian')
        if self.is_vegan:
            restrictions.append('vegan')
        if self.is_gluten_free:
            restrictions.append('gluten_free')
        if self.is_dairy_free:
            restrictions.append('dairy_free')
        return restrictions


class Ingredient(models.Model):
    """
    材料モデル（拡張版）
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=200, verbose_name='材料名')
    quantity = models.CharField(max_length=100, verbose_name='分量（例: 1個, 100g）')
    
    # 材料カテゴリ
    category = models.CharField(
        max_length=30,
        choices=[
            ('protein', 'タンパク質源'),
            ('carb', '炭水化物源'),
            ('vegetable', '野菜'),
            ('fruit', '果物'),
            ('dairy', '乳製品'),
            ('fat', '油脂'),
            ('seasoning', '調味料'),
            ('other', 'その他')
        ],
        default='other',
        verbose_name='材料カテゴリ'
    )
    
    # 材料の栄養情報（任意）
    calories_per_unit = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='単位あたりカロリー'
    )
    
    # アレルゲン情報
    contains_gluten = models.BooleanField(default=False, verbose_name='グルテン含有')
    contains_dairy = models.BooleanField(default=False, verbose_name='乳製品含有')
    contains_nuts = models.BooleanField(default=False, verbose_name='ナッツ類含有')
    contains_soy = models.BooleanField(default=False, verbose_name='大豆含有')
    
    is_optional = models.BooleanField(default=False, verbose_name='オプション材料')
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.quantity}) for {self.recipe.title}"


class NutritionProfile(models.Model):
    """
    ユーザーの詳細栄養プロフィール
    """
    user = models.OneToOneField(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='nutrition_profile'
    )
    
    # 詳細目標値
    target_fiber = models.FloatField(default=25.0, verbose_name='食物繊維目標 (g)')
    target_sodium_max = models.FloatField(default=2300.0, verbose_name='ナトリウム上限 (mg)')
    target_sugar_max = models.FloatField(default=50.0, verbose_name='糖質上限 (g)')
    
    # ビタミン・ミネラル目標
    target_calcium = models.FloatField(default=800.0, verbose_name='カルシウム目標 (mg)')
    target_iron = models.FloatField(default=10.0, verbose_name='鉄分目標 (mg)')
    target_vitamin_c = models.FloatField(default=100.0, verbose_name='ビタミンC目標 (mg)')
    
    # 最適化設定
    optimization_weights = models.JSONField(
        default=dict,
        verbose_name='最適化重み',
        help_text='各栄養素の重要度設定'
    )
    
    # 食事制限
    dietary_restrictions = models.JSONField(
        default=list,
        verbose_name='食事制限',
        help_text='アレルギーや食事制限のリスト'
    )
    
    # 予算制約
    daily_budget_max = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, blank=True,
        verbose_name='1日の食費上限 (円)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}の栄養プロフィール"
    
    @property
    def complete_targets(self):
        """完全な栄養目標辞書を返す"""
        basic_profile = getattr(self.user, 'userprofile', None)
        
        return {
            'protein': basic_profile.target_protein if basic_profile else 70,
            'fat': basic_profile.target_fat if basic_profile else 60,
            'carbohydrate': basic_profile.target_carbohydrate if basic_profile else 250,
            'calories': getattr(basic_profile, 'target_calories', 2000) if basic_profile else 2000,
            'fiber': self.target_fiber,
            'sodium_max': self.target_sodium_max,
            'sugar_max': self.target_sugar_max,
            'calcium': self.target_calcium,
            'iron': self.target_iron,
            'vitamin_c': self.target_vitamin_c
        }