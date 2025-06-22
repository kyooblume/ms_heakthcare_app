# meals/views.py
from rest_framework import viewsets, filters # ← filters をインポートに追加
from rest_framework.permissions import IsAuthenticated
from .models import MealLog, FoodMaster # ← FoodMaster をインポートに追加
from .serializers import MealLogSerializer, FoodMasterSerializer # ← FoodMasterSerializer をインポートに追加


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