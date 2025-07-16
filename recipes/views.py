# recipes/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
# ↓ データベースの計算で使う、便利な機能をインポートします
from django.db.models import Sum, F
from django.db.models.functions import Abs

from .models import Recipe
from .serializers import RecipeSerializer
from meals.models import MealItem

class SuggestRecipeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.userprofile
        today = timezone.now().date()

        # 1. 今日の栄養摂取量を計算
        todays_items = MealItem.objects.filter(meal__user=user, meal__recorded_at__date=today)
        actual_protein = todays_items.aggregate(total=Sum('protein'))['total'] or 0

        # 2. 不足している栄養素を特定
        protein_deficit = (profile.target_protein or 70) - actual_protein

        # 3. もしタンパク質が不足していれば...
        if protein_deficit > 10: # 10g以上不足している場合
            message = f"タンパク質が約{int(protein_deficit)}g不足しています。こんな料理はいかがですか？"

            # --- ★ここからが新しいロジック ---
            # 4. 「ちょうど良い」範囲のレシピを探す
            # 例：不足分(20g)の80%～150%のタンパク質を含むレシピを探す
            ideal_min = protein_deficit * 0.8
            ideal_max = protein_deficit * 1.5
            
            # まずは理想的な範囲のレシピ候補を取得
            suggested_recipes = Recipe.objects.filter(
                total_protein__gte=ideal_min,
                total_protein__lte=ideal_max
            )

            # 5. 候補の中から、不足分に「最も近い」レシピを選ぶ
            #    Abs()は絶対値を計算する機能。差が小さい順に並べ替える
            if suggested_recipes.exists():
                suggested_recipes = suggested_recipes.annotate(
                    diff=Abs(F('total_protein') - protein_deficit)
                ).order_by('diff')[:3] # 差が小さい上位3件を提案
            else:
                # 理想的なレシピがなければ、これまで通りタンパク質が多いものを提案
                suggested_recipes = Recipe.objects.order_by('-total_protein')[:3]
            # --- ★ここまでが新しいロジック ---

        else:
            # 足りている場合は、汎用的なおすすめを提案
            message = "栄養バランスは良い調子です！こんな料理はいかがですか？"
            suggested_recipes = Recipe.objects.order_by('?')[:3] # ランダムに3件

        serializer = RecipeSerializer(suggested_recipes, many=True)
        response_data = {
            "message": message,
            "suggestions": serializer.data
        }
        return Response(response_data)