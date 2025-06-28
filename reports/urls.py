# reports/urls.py
from django.urls import path
from .views import StepRankingReportView, SocialJetlagReportView

app_name = 'reports'  # ← ★この一行を追加してください

urlpatterns = [
    path('steps-ranking/<str:date_str>/', StepRankingReportView.as_view(), name='steps-ranking-report'),
    path('sleep-rhythm-ranking/', SocialJetlagReportView.as_view(), name='sleep-rhythm-ranking'),
]