# health_records/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 必要なビューをまとめてインポートします
from .views import (
    HealthRecordViewSet,
    SleepRecordViewSet,
    SleepSessionViewSet,
    SleepChronotypeSurveyViewSet, # このViewSetも登録が必要だと思われます
    HealthSummaryView,
    StepCountRankingView
)

# --- ルーターの設定 ---
router = DefaultRouter()

# 各ViewSetをルーターに登録します
# 重複していた'records'の登録を1つにまとめます
router.register(r'records', HealthRecordViewSet, basename='healthrecord')
router.register(r'sleep', SleepRecordViewSet, basename='sleeprecord')
router.register(r'sleep-sessions', SleepSessionViewSet, basename='sleepsession')
# 不足していたSleepChronotypeSurveyViewSetを登録します
router.register(r'sleep-surveys', SleepChronotypeSurveyViewSet, basename='sleepchronotypesurvey')


# --- URLパターンの定義 ---
app_name = 'health_records'

urlpatterns = [
    # ViewSetに基づかないカスタムURLを先に定義します
    path('summary/', HealthSummaryView.as_view(), name='health-summary'),
    path('steps/ranking/<str:date_str>/', StepCountRankingView.as_view(), name='steps-ranking'),
    
    # ルーターが自動生成したURLを最後にまとめてインクルードします
    path('', include(router.urls)),
]