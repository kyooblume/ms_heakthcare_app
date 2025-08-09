# recipes/urls.py

from django.urls import path
from django.http import JsonResponse
from django.views import View
from .views import SuggestRecipeView, DinnerSuggestionView, OptimizedPlanView

# デバッグ用ビュー
class DebugView(View):
    def get(self, request):
        return JsonResponse({
            "message": "レシピAPIは正常に動作しています",
            "path": request.path,
            "method": request.method,
            "available_endpoints": [
                "/api/recipes/debug/",
                "/api/recipes/suggestions/", 
                "/api/recipes/suggest-dinner/",
                "/api/recipes/optimized-plan/"
            ]
        })

class SimpleTestView(View):
    def get(self, request):
        return JsonResponse({
            "status": "success",
            "message": "シンプルテストが成功しました",
            "path": request.path,
            "method": request.method
        })

# 認証なしのテスト用提案ビュー
class TestSuggestRecipeView(View):
    def get(self, request):
        from .models import Recipe
        try:
            # レシピが存在するかチェック
            recipe_count = Recipe.objects.count()
            if recipe_count == 0:
                return JsonResponse({
                    "error": "レシピが登録されていません",
                    "recipe_count": recipe_count
                })
            
            # 簡単なレシピリストを返す
            recipes = Recipe.objects.all()[:3]
            recipe_data = []
            for recipe in recipes:
                recipe_data.append({
                    "title": recipe.title,
                    "total_calories": recipe.total_calories,
                    "total_protein": recipe.total_protein,
                    "total_fat": recipe.total_fat,
                    "total_carbohydrates": recipe.total_carbohydrates
                })
            
            return JsonResponse({
                "message": "テスト用レシピ提案",
                "suggestions": recipe_data,
                "recipe_count": recipe_count
            })
            
        except Exception as e:
            return JsonResponse({
                "error": f"エラーが発生しました: {str(e)}",
                "type": str(type(e).__name__)
            })

urlpatterns = [
    path('debug/', DebugView.as_view(), name='recipe-debug'),
    path('test/', SimpleTestView.as_view(), name='recipe-test'),
    path('test-suggestions/', TestSuggestRecipeView.as_view(), name='test-recipe-suggestions'),
    path('suggestions/', SuggestRecipeView.as_view(), name='recipe-suggestions'),
    path('suggest-dinner/', DinnerSuggestionView.as_view(), name='suggest-dinner'),
    path('optimized-plan/', OptimizedPlanView.as_view(), name='optimized-plan'),
]