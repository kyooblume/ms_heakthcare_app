# meals/serializers.py
from rest_framework import serializers
from .models import MealLog, FoodMaster,MealComponent


class FoodMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodMaster
        # foodmasterの全てのフィールドをAPIで返すように設定
        fields = '__all__'

class MealComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealComponent
        fields = ['food', 'quantity']
# meals/serializers.py

# ... (MealComponentSerializer の下) ...

# --- ★MealLogSerializer をこの内容に書き換える ---
class MealLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    # ↓ components を書き込み可能(write_only)なネストしたシリアライザーとして定義
    components = MealComponentSerializer(many=True, write_only=True)

    # ↓ 新しく、計算結果を表示するためのフィールドを追加（読み取り専用）
    total_calories = serializers.SerializerMethodField()
    total_protein = serializers.SerializerMethodField()

    class Meta:
        model = MealLog
        fields = [
            'id', 'user_username', 'meal_type', 'notes', 'eaten_at', 
            'components', # ← 書き込み用
            'total_calories', 'total_protein' # ← 読み取り用
        ]

    # --- ↓ 計算結果を返すためのメソッド ---
    def get_total_calories(self, obj):
        # obj は MealLog インスタンス
        total = 0
        for component in obj.components.all():
            total += (component.food.calories_per_100g * component.quantity / 100)
        return round(total)

    def get_total_protein(self, obj):
        total = 0
        for component in obj.components.all():
            total += (component.food.protein_per_100g * component.quantity / 100)
        return round(total, 1)

    # --- ↓ データ作成時のカスタムロジック ---
    def create(self, validated_data):
        # 'components' のデータを取り出す
        components_data = validated_data.pop('components')
        # 先に MealLog の大枠を作成
        meal_log = MealLog.objects.create(**validated_data)
        # 次に、各componentsのデータを使ってMealComponentを作成
        for component_data in components_data:
            MealComponent.objects.create(meal_log=meal_log, **component_data)
        return meal_log
