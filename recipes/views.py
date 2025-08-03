from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, F, Q, FloatField
from django.db.models.functions import Abs, Coalesce
from .models import Recipe
from .serializers import RecipeSerializer
from meals.models import MealItem
from .optimization import optimize_meal_plan # 作成した最適化エンジンをインポート

class SuggestRecipeView(APIView):
    """
    ユーザーの栄養摂取状況と優先順位設定に基づき、
    最適な献立を提案するAPIビュー。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from accounts.models import UserProfile
        try:
            user = request.user
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"error": "ユーザープロフィールが見つかりません。"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()

        # 1. ユーザーの目標値を取得 (目標がなければデフォルト値を設定)
        targets = {
            'protein': profile.target_protein or 70.0,
            'fat': profile.target_fat or 60.0,
            'carbohydrate': profile.target_carbohydrate or 250.0,
        }

        # 2. 今日の実績摂取量を計算
        todays_items = MealItem.objects.filter(meal__user=user, meal__recorded_at__date=today)
        actuals = todays_items.aggregate(
            protein=Coalesce(Sum('protein'), 0.0, output_field=FloatField()),
            fat=Coalesce(Sum('fat'), 0.0, output_field=FloatField()),
            carbohydrates=Coalesce(Sum('carbohydrates'), 0.0, output_field=FloatField())
        )

        # 3. 各栄養素の「不足量」と「不足率」を計算
        deficits = {
            'protein': targets['protein'] - actuals['protein'],
            'fat': targets['fat'] - actuals['fat'],
            'carbohydrate': targets['carbohydrate'] - actuals['carbohydrates'],
        }
        
        # 10g以上不足している栄養素をリストアップ
        lacking_nutrients = {k: v for k, v in deficits.items() if v > 10}
#要krン頭
        if not lacking_nutrients:
            # 不足がなければ、汎用的なおすすめを提案
            message = "栄養バランスは良い調子です！こんな料理はいかがですか？"
            suggested_recipes = Recipe.objects.order_by('?')[:5]
        else:
            # ユーザーの優先順位設定を取得
            priority = profile.nutrition_priority

            # 4. ユーザーの優先順位に応じて、レシピの評価方法を切り替え
            if priority == 'protein_first':
                message = "タンパク質を最優先で補給しましょう！"
                suggested_recipes = Recipe.objects.order_by('-total_protein')[:5]

            elif priority == 'low_calorie':
                message = "カロリーを抑えつつ、栄養を補える献立はこちらです。"
                # カロリーが低く、かつ不足栄養素をある程度補えるものを探す
                suggested_recipes = Recipe.objects.filter(
                    Q(total_protein__gte=deficits.get('protein', 0) * 0.5) |
                    Q(total_fat__gte=deficits.get('fat', 0) * 0.5) |
                    Q(total_carbohydrates__gte=deficits.get('carbohydrate', 0) * 0.5)
                ).order_by('total_calories')[:5]
            
            else: # デフォルトは 'balance' (全体的なバランスを重視)
                # 不足率が最も高い「メインターゲット」を特定
                deficiency_ratios = {
                    nutrient: (deficits[nutrient] / targets[nutrient])
                    for nutrient in lacking_nutrients
                }
                main_target_nutrient = max(deficiency_ratios, key=deficiency_ratios.get)
                message = f"{main_target_nutrient.capitalize()} が特に不足しています。バランスを考えて、こんな料理はいかがですか？"

                # 総合スコアでレシピを評価し、上位を提案
                suggested_recipes = Recipe.objects.annotate(
                    # メインターゲットの充足度 (50点満点)
                    main_score=50.0 * (F(f'total_{main_target_nutrient}') / deficits[main_target_nutrient]),
                    # 他の不足栄養素の充足度 (それぞれ25点満点)
                    protein_score=25.0 * (F('total_protein') / deficits.get('protein', 1.0)),
                    fat_score=25.0 * (F('total_fat') / deficits.get('fat', 1.0)),
                    carb_score=25.0 * (F('total_carbohydrates') / deficits.get('carbohydrate', 1.0))
                ).annotate(
                    # 総合スコアを計算
                    total_score=F('main_score') +
                                (F('protein_score') if 'protein' in lacking_nutrients else 0) +
                                (F('fat_score') if 'fat' in lacking_nutrients else 0) +
                                (F('carb_score') if 'carbohydrate' in lacking_nutrients else 0)
                ).order_by('-total_score')[:5]

        serializer = RecipeSerializer(suggested_recipes, many=True)
        response_data = {
            "message": message,
            "suggestions": serializer.data
        }
        return Response(response_data)
    

class OptimizedPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.userprofile
        
        # (ここでは簡略化のため、1日の目標をそのまま渡す)
        targets = {
            'protein': profile.target_protein or 70,
            'fat': profile.target_fat or 60,
            'carbohydrate': profile.target_carbohydrate or 250,
        }

        plan, message = optimize_meal_plan(targets)

        if plan is not None:
            serializer = RecipeSerializer([item['recipe'] for item in plan], many=True)
            
            # レシピ情報に、食べるべき量(quantity)を追加して返す
            response_data = []
            for i, recipe_data in enumerate(serializer.data):
                recipe_data['recommended_quantity'] = plan[i]['quantity']
                response_data.append(recipe_data)

            return Response({
                "message": message,
                "plan": response_data
            })
        else:
            return Response({"error": message}, status=status.HTTP_404_NOT_FOUND)




class DinnerSuggestionView(APIView):
    """
    データベースに記録された、その日の朝食と昼食の情報を元に、
    夜ご飯に最適な献立を提案するAPIビュー。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request): # POSTからGETに変更
        user = request.user
        profile = user.userprofile
        today = timezone.now().date()

        # 1. 今日の「朝食」と「昼食」の記録をデータベースから取得
        consumed_items = MealItem.objects.filter(
            meal__user=user,
            meal__recorded_at__date=today,
            meal__meal_type__in=['breakfast', 'lunch']
        )
        
        # 2. 食べたものの栄養素を合計する
        consumed_nutrients = consumed_items.aggregate(
            protein=Sum('protein'),
            fat=Sum('fat'),
            carbohydrates=Sum('carbohydrates')
        )
        
        # 3. 1日の目標値から、食べた分を差し引き、「夜ご飯で摂るべき栄養素」を計算
        remaining_targets = {
            'protein': (profile.target_protein or 70) - (consumed_nutrients.get('protein') or 0),
            'fat': (profile.target_fat or 60) - (consumed_nutrients.get('fat') or 0),
            'carbohydrate': (profile.target_carbohydrate or 250) - (consumed_nutrients.get('carbohydrate') or 0),
        }

        # 4. 「夜ご飯の目標」に最も近いレシピを探す (SuggestRecipeViewのロジックを応用)
        if remaining_targets['protein'] > 10: # タンパク質が10g以上不足している場合
            suggested_recipes = Recipe.objects.annotate(
                diff=Abs(F('total_protein') - remaining_targets['protein'])
            ).order_by('diff')[:3]
            message = f"夜ご飯でタンパク質を約{int(remaining_targets['protein'])}g摂るのがおすすめです。"
        else:
            suggested_recipes = Recipe.objects.order_by('total_calories')[:3]
            message = "順調ですね！夜ご飯は軽めにいかがですか？"

        serializer = RecipeSerializer(suggested_recipes, many=True)
        return Response({
            "message": message,
            "remaining_targets": remaining_targets,
            "suggestions": serializer.data
        })
    

#

# ... (SuggestRecipeViewはそのまま) ...

# --- ★ここから新しいAPIビューを追加 ---
class OptimizedPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.userprofile
        
        # (ここでは簡略化のため、1日の目標をそのまま渡す)
        targets = {
            'protein': profile.target_protein or 70,
            'fat': profile.target_fat or 60,
            'carbohydrate': profile.target_carbohydrate or 250,
        }

        plan, message = optimize_meal_plan(targets)

        if plan is not None:
            serializer = RecipeSerializer([item['recipe'] for item in plan], many=True)
            
            # レシピ情報に、食べるべき量(quantity)を追加して返す
            response_data = []
            for i, recipe_data in enumerate(serializer.data):
                recipe_data['recommended_quantity'] = plan[i]['quantity']
                response_data.append(recipe_data)

            return Response({
                "message": message,
                "plan": response_data
            })
        else:
            return Response({"error": message}, status=status.HTTP_404_NOT_FOUND)