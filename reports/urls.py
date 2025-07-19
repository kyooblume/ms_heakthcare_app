# reports/urls.py
from django.urls import path
from .views import StepRankingReportView, SocialJetlagReportView, DailyActivityReportView, WeeklySleepReportView, SocialJetlagReportView, DashboardSummaryView

app_name = 'reports'

app_name = 'reports'  # ← ★この一行を追加してください

urlpatterns = [
    path('steps-ranking/<str:date_str>/', StepRankingReportView.as_view(), name='steps-ranking-report'),
    path('sleep-rhythm-ranking/', SocialJetlagReportView.as_view(), name='sleep-rhythm-ranking'),
    path('activity/daily/<str:date_str>/', DailyActivityReportView.as_view(), name='daily-activity-report'),
    path('sleep/weekly/', WeeklySleepReportView.as_view(), name='weekly-sleep-report'),
]
