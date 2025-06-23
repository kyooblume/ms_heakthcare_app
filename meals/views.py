# meals/views.py

from django.shortcuts import render # これは元々あるかもしれません
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import MealLog, FoodMaster
from .serializers import MealLogSerializer, FoodMasterSerializer

# --- 新しいレポート機能で使うインポート文 ---
from rest_framework.views import APIView
from rest_framework.response import Response # ← ★この行を追加・確認してください
from rest_framework import status
from datetime import datetime
from django.utils import timezone
from django.db.models import Sum, Avg, Max, Min


# ... (これ以降に、FoodMasterViewSet, MealLogViewSet, DailyNutritionReportView などのクラス定義) ...
# --- ★ここから新しい FoodMasterViewSet を追加 ---
class FoodMasterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    食品マスターデータを名前で検索・閲覧するための読み取り専用APIビュー。
    """
    queryset = FoodMaster.objects.all().order_by('id') # 全ての食品データを対象にする
    serializer_class = FoodMasterSerializer
    permission_classes = [IsAuthenticated] # ログインしているユーザーのみ検索可能
    
    # --- ★ここが検索機能のキーポイント ---
    filter_backends = [filters.SearchFilter]
    search_fields = ['name'] # 'name' フィールドを対象に部分一致検索を可能にする

class MealLogViewSet(viewsets.ModelViewSet):
    """
    食事記録のCRUD操作を行うためのAPIビューセット。
    認証されたユーザーは、自身の食事記録のみを操作できる。
    """
    serializer_class = MealLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        現在のリクエストユーザーに紐づく食事記録のみを返す。
        """
        return MealLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        新しい食事記録を作成する際に、現在のユーザーを自動的に紐付ける。
        """
        serializer.save(user=self.request.user)


  

# --- ★ここから新しいビューを追加 ---
class DailyNutritionReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        try:
            # URLから受け取った日付文字列を日付オブジェクトに変換
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "無効な日付形式です。YYYY-MM-DDで指定してください。"}, status=400)

        user = request.user
        profile = user.profile

        # その日の食事記録を取得
        meal_logs = MealLog.objects.filter(user=user, eaten_at__date=target_date)

        # 栄養素の合計を計算
        actual_calories = 0
        actual_protein = 0
        # ... (他の栄養素も同様に合計)
        for log in meal_logs:
            for component in log.components.all():
                # 食べた量(g)に応じて栄養素を計算
                ratio = component.quantity / 100.0
                actual_calories += component.food.calories_per_100g * ratio
                actual_protein += component.food.protein_per_100g * ratio
                # ...

        # レスポンスデータを作成
        response_data = {
            "date": target_date,
            "summary": {
                "calories": {"target": profile.target_calories, "actual": round(actual_calories), "balance": round(actual_calories - (profile.target_calories or 0))},
                "protein": {"target": profile.target_protein, "actual": round(actual_protein, 1), "balance": round(actual_protein - (profile.target_protein or 0), 1)},
                # ...
            }
        }
        return Response(response_data)