# accounts/urls.py

from django.urls import path, include # ← include をインポート
from rest_framework.routers import DefaultRouter # ← ルーターをインポート
from .views import UserRegistrationView, UserProfileView, UserDeviceViewSet, PasswordChangeView
app_name = 'accounts'

# --- ルーターの設定 ---
# DefaultRouterのインスタンスを作成
router = DefaultRouter()
# 'devices' というURLで UserDeviceViewSet を登録
router.register(r'devices', UserDeviceViewSet, basename='userdevice')

# --- 全体のURLパターン ---
urlpatterns = [
    # 既存のパス (register, profile) はそのまま
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    # ★ルーターが自動生成したURLを、この場所に追加
    path('', include(router.urls)),
]