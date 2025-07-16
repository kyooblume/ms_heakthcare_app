# surveys/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Survey, Answer
from .serializers import SurveySerializer, AnswerSerializer

class SurveyViewSet(viewsets.ReadOnlyModelViewSet):
    """アンケートの一覧・詳細を取得するためのAPI"""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

class AnswerViewSet(viewsets.ModelViewSet):
    """アンケートへの回答を作成・閲覧するためのAPI"""
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 自分の回答のみを閲覧可能にする
        return Answer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 回答者として、現在ログインしているユーザーを自動で設定
        serializer.save(user=self.request.user)