# meals/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MealLog
from .serializers import MealLogSerializer

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