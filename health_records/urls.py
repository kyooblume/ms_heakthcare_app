# health_records/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter # ルーターをインポート
from .views import HealthRecordViewSet # 先ほど作成したHealthRecordViewSetをインポート
from .views import HealthRecordViewSet, HealthSummaryView 

# DefaultRouterのインスタンスを作成
router = DefaultRouter()

# HealthRecordViewSetをルーターに登録
# 'records' がこのビューセットのURLのプレフィックスになります。
# 例: /api/health/records/ や /api/health/records/{pk}/ など
router.register(r'records', HealthRecordViewSet, basename='healthrecord')
# basenameは、querysetがビューセットに直接定義されていない場合や、
# URLの名前をカスタマイズしたい場合に指定します。
# 通常、ModelViewSetでquerysetが設定されていれば自動で推測されますが、
# 明示しておくと確実です。

app_name = 'health_records' # アプリケーションの名前空間を定義（推奨）

urlpatterns = [
    # router.urls で生成されたURLパターンをこのリストに含めます
    path('summary/', HealthSummaryView.as_view(), name='health-summary'),
    path('', include(router.urls)),
]