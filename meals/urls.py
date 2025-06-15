# meals/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealLogViewSet

# ルーターを初期化
router = DefaultRouter()
# 'logs' というURLで MealLogViewSet を登録
router.register(r'logs', MealLogViewSet, basename='meallog')

app_name = 'meals'

urlpatterns = [
    # ルーターが自動生成したURLを urlpatterns に含める
    path('', include(router.urls)),
]