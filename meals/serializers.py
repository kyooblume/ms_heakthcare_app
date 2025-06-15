# meals/serializers.py
from rest_framework import serializers
from .models import MealLog

class MealLogSerializer(serializers.ModelSerializer):
    # レスポンスにユーザー名を含めるための、読み取り専用フィールド
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MealLog
        # APIでやり取りするフィールドをすべて指定
        fields = [
            'id',
            'user',
            'user_username',
            'meal_type',
            'get_meal_type_display', # meal_typeの表示名（例: '朝食'）
            'meal_name',
            'calories',
            'protein',
            'fat',
            'carbohydrate',
            'notes',
            'eaten_at',
        ]
        # ユーザーはビューで自動設定するので、クライアントからは送れないように読み取り専用にする
        read_only_fields = ('user', 'user_username', 'get_meal_type_display')