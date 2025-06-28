# meals/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealLogViewSet, FoodMasterViewSet, DailyNutritionReportView,AddMealFromBarcodeView

router = DefaultRouter()
router.register(r'logs', MealLogViewSet, basename='meallog')
router.register(r'foods', FoodMasterViewSet, basename='foodmaster') # ← ★この行を追加

app_name = 'meals'

urlpatterns = [
    path('add-from-barcode/', AddMealFromBarcodeView.as_view(), name='meal-add-from-barcode'),
    path('reports/daily/<str:date_str>/', DailyNutritionReportView.as_view(), name='daily-nutrition-report'),
    path('', include(router.urls)),
]

