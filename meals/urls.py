# meals/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealLogViewSet, FoodMasterViewSet,AddMealFromBarcodeView
from .views import MealLogViewSet, AddMealFromBarcodeView, DailyNutritionSummaryView # 新しいビューをインポート
router = DefaultRouter()
router.register(r'logs', MealLogViewSet, basename='meallog')
router.register(r'foods', FoodMasterViewSet, basename='foodmaster') # ← ★この行を追加

app_name = 'meals'

urlpatterns = [
    path('add-from-barcode/', AddMealFromBarcodeView.as_view(), name='meal-add-from-barcode'),

    path('summary/daily/<str:date_str>/', DailyNutritionSummaryView.as_view(), name='daily-nutrition-summary'),
    path('', include(router.urls)),
]


