# meals/serializers.py
from rest_framework import serializers
from .models import MealLog, FoodMaster, MealComponent, Meal, MealItem


class FoodMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodMaster
        fields = '__all__'


class MealComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealComponent
        fields = ['food', 'quantity']


class MealLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    # componentsを書き込み可能(write_only)なネストしたシリアライザーとして定義
    components = MealComponentSerializer(many=True, write_only=True)

    # 計算結果を表示するためのフィールドを追加（読み取り専用）
    total_calories = serializers.SerializerMethodField()
    total_protein = serializers.SerializerMethodField()

    class Meta:
        model = MealLog
        fields = [
            'id', 'user_username', 'meal_type', 'notes', 'eaten_at', 
            'components',  # 書き込み用
            'total_calories', 'total_protein'  # 読み取り用
        ]

    def get_total_calories(self, obj):
        """合計カロリーを計算"""
        total = 0
        for component in obj.components.all():
            total += (component.food.calories_per_100g * component.quantity / 100)
        return round(total)

    def get_total_protein(self, obj):
        """合計タンパク質を計算"""
        total = 0
        for component in obj.components.all():
            total += (component.food.protein_per_100g * component.quantity / 100)
        return round(total, 1)

    def create(self, validated_data):
        """データ作成時のカスタムロジック"""
        # 'components'のデータを取り出す
        components_data = validated_data.pop('components')
        # 先にMealLogの大枠を作成
        meal_log = MealLog.objects.create(**validated_data)
        # 次に、各componentsのデータを使ってMealComponentを作成
        for component_data in components_data:
            MealComponent.objects.create(meal_log=meal_log, **component_data)
        return meal_log


# バーコード機能用のシリアライザー
class MealItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealItem
        fields = '__all__'


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Meal
        fields = ['id', 'user', 'meal_type', 'notes', 'recorded_at', 'items']