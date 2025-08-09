# meals/serializers.py
from rest_framework import serializers
from .models import MealLog, FoodMaster, MealComponent, Meal, MealItem


class FoodMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodMaster
        fields = '__all__'


class MealComponentSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source='food.name', read_only=True)
    calculated_calories = serializers.SerializerMethodField()
    calculated_protein = serializers.SerializerMethodField()
    calculated_fat = serializers.SerializerMethodField()
    calculated_carbohydrate = serializers.SerializerMethodField()

    class Meta:
        model = MealComponent
        fields = ['id', 'food', 'food_name', 'quantity', 
                 'calculated_calories', 'calculated_protein', 
                 'calculated_fat', 'calculated_carbohydrate']

    def get_calculated_calories(self, obj):
        if obj.food and obj.quantity:
            return round((obj.food.calories_per_100g * obj.quantity) / 100)
        return 0

    def get_calculated_protein(self, obj):
        if obj.food and obj.quantity:
            return round((obj.food.protein_per_100g * obj.quantity) / 100, 1)
        return 0

    def get_calculated_fat(self, obj):
        if obj.food and obj.quantity:
            return round((obj.food.fat_per_100g * obj.quantity) / 100, 1)
        return 0

    def get_calculated_carbohydrate(self, obj):
        if obj.food and obj.quantity:
            return round((obj.food.carbohydrate_per_100g * obj.quantity) / 100, 1)
        return 0


class MealLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    components = MealComponentSerializer(many=True, read_only=True)
    components_input = MealComponentSerializer(many=True, write_only=True, source='components')

    # 計算結果を表示するためのフィールド
    total_calories = serializers.SerializerMethodField()
    total_protein = serializers.SerializerMethodField()
    total_fat = serializers.SerializerMethodField()
    total_carbohydrate = serializers.SerializerMethodField()

    class Meta:
        model = MealLog
        fields = [
            'id', 'user_username', 'meal_type', 'notes', 'eaten_at', 
            'components',  # 読み取り用
            'components_input',  # 書き込み用
            'total_calories', 'total_protein', 'total_fat', 'total_carbohydrate'
        ]

    def get_total_calories(self, obj):
        """合計カロリーを計算"""
        total = 0
        for component in obj.components.all():
            if component.food and component.quantity:
                total += (component.food.calories_per_100g * component.quantity / 100)
        return round(total)

    def get_total_protein(self, obj):
        """合計タンパク質を計算"""
        total = 0
        for component in obj.components.all():
            if component.food and component.quantity:
                total += (component.food.protein_per_100g * component.quantity / 100)
        return round(total, 1)

    def get_total_fat(self, obj):
        """合計脂質を計算"""
        total = 0
        for component in obj.components.all():
            if component.food and component.quantity:
                total += (component.food.fat_per_100g * component.quantity / 100)
        return round(total, 1)

    def get_total_carbohydrate(self, obj):
        """合計炭水化物を計算"""
        total = 0
        for component in obj.components.all():
            if component.food and component.quantity:
                total += (component.food.carbohydrate_per_100g * component.quantity / 100)
        return round(total, 1)

    def create(self, validated_data):
        """データ作成時のカスタムロジック"""
        components_data = validated_data.pop('components', [])
        meal_log = MealLog.objects.create(**validated_data)
        
        for component_data in components_data:
            MealComponent.objects.create(meal_log=meal_log, **component_data)
        return meal_log

    def update(self, instance, validated_data):
        """データ更新時のカスタムロジック"""
        components_data = validated_data.pop('components', None)
        
        # 基本フィールドを更新
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # コンポーネントを更新
        if components_data is not None:
            instance.components.all().delete()  # 既存のコンポーネントを削除
            for component_data in components_data:
                MealComponent.objects.create(meal_log=instance, **component_data)
        
        return instance


# バーコード機能用のシリアライザー（既存のまま）
class MealItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealItem
        fields = '__all__'


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Meal
        fields = ['id', 'user', 'meal_type', 'notes', 'recorded_at', 'items']