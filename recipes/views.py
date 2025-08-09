# recipes/views.py - 修正版

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
from .optimization import optimize_meal_plan, NutritionOptimizer
from accounts.models import UserProfile
import logging

logger = logging.getLogger(__name__)

class SuggestRecipeView(APIView):
    """
    線形計画法ベースの高度な栄養最適化システム
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            profile = user.profile
        except (UserProfile.DoesNotExist, AttributeError):
            return Response({"error": "ユーザープロフィールが見つかりません。"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()

        # 1. ユーザーの目標値を取得
        targets = {
            'protein': profile.target_protein or 70.0,
            'fat': profile.target_fat or 60.0,
            'carbohydrate': profile.target_carbohydrate or 250.0,
            'calories': getattr(profile, 'target_calories', None) or 2000.0,
        }

        # 2. 今日の実績摂取量を計算
        current_intake = self._get_current_intake(user, today)

        # 3. ユーザーの優先順位に基づいて最適化目標を設定
        priority = getattr(profile, 'nutrition_priority', 'balance')
        optimization_goal = self._map_priority_to_goal(priority)

        # 4. 線形計画法による最適化を実行
        try:
            optimizer = NutritionOptimizer()
            result = optimizer.optimize_daily_meal(
                targets=targets,
                current_intake=current_intake,
                constraints=self._get_user_constraints(profile)
            )
            
            if result[0] is not None:
                return self._format_optimization_response(result, targets, current_intake)
            else:
                # 最適化に失敗した場合のフォールバック
                return self._fallback_suggestions(targets, current_intake)
                
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return self._fallback_suggestions(targets, current_intake)

    def _get_current_intake(self, user, today):
        """今日の現在摂取量を計算"""
        todays_items = MealItem.objects.filter(meal__user=user, meal__recorded_at__date=today)
        actuals = todays_items.aggregate(
            protein=Coalesce(Sum('protein'), 0.0, output_field=FloatField()),
            fat=Coalesce(Sum('fat'), 0.0, output_field=FloatField()),
            carbohydrates=Coalesce(Sum('carbohydrates'), 0.0, output_field=FloatField()),
            calories=Coalesce(Sum('calories'), 0.0, output_field=FloatField())
        )
        
        return {
            'protein': actuals['protein'],
            'fat': actuals['fat'],
            'carbohydrate': actuals['carbohydrates'],
            'calories': actuals['calories']
        }

    def _map_priority_to_goal(self, priority):
        """ユーザー優先順位を最適化目標にマッピング"""
        mapping = {
            'protein_first': 'high_protein',
            'low_calorie': 'low_calorie',
            'balance': 'balanced'
        }
        return mapping.get(priority, 'balanced')

    def _get_user_constraints(self, profile):
        """ユーザー固有の制約を取得"""
        constraints = {}
        
        # アレルギーや食事制限があれば追加
        if hasattr(profile, 'max_sodium'):
            constraints['max_sodium'] = profile.max_sodium
        
        if hasattr(profile, 'min_meals_per_day'):
            constraints['min_meals'] = profile.min_meals_per_day
            
        return constraints

    def _format_optimization_response(self, optimization_result, targets, current_intake):
        """最適化結果をAPI応答形式にフォーマット"""
        result, message = optimization_result
        
        # レシピデータをシリアライズ
        recipes = [item['recipe'] for item in result['meal_plan']]
        serializer = RecipeSerializer(recipes, many=True)
        
        # 数量情報を追加
        suggestions = []
        for i, recipe_data in enumerate(serializer.data):
            meal_item = result['meal_plan'][i]
            recipe_data['recommended_quantity'] = meal_item['quantity']
            recipe_data['nutrition_contribution'] = meal_item.get('nutrition_contribution', {})
            suggestions.append(recipe_data)

        return Response({
            "message": message,
            "suggestions": suggestions,
            "optimization_summary": {
                "total_nutrition": result.get('total_nutrition', {}),
                "achievement_rates": result.get('achievement_rates', {}),
                "current_intake": current_intake,
                "targets": targets,
                "remaining_targets": {
                    key: max(0, targets[key] - current_intake[key]) 
                    for key in targets.keys() 
                    if key in current_intake
                }
            },
            "is_optimized": True,
            "optimization_status": result.get('optimization_status', 'Success')
        })

    def _fallback_suggestions(self, targets, current_intake):
        """最適化失敗時のフォールバック提案"""
        # 不足栄養素を特定
        deficits = {
            key: targets[key] - current_intake.get(key, 0)
            for key in targets.keys()
        }
        
        lacking_nutrients = {k: v for k, v in deficits.items() if v > 10}
        
        if not lacking_nutrients:
            suggested_recipes = Recipe.objects.order_by('?')[:5]
            message = "栄養バランスは良好です！バラエティ豊かな料理はいかがですか？"
        else:
            # 最も不足している栄養素に焦点を当てる
            main_deficit = max(lacking_nutrients.items(), key=lambda x: x[1])
            nutrient_name = main_deficit[0]
            
            if nutrient_name == 'protein':
                suggested_recipes = Recipe.objects.order_by('-total_protein')[:5]
                message = f"タンパク質が約{main_deficit[1]:.0f}g不足しています。高タンパク食品をおすすめします。"
            elif nutrient_name == 'fat':
                suggested_recipes = Recipe.objects.order_by('-total_fat')[:5]
                message = f"脂質が約{main_deficit[1]:.0f}g不足しています。良質な脂質を含む食品をおすすめします。"
            elif nutrient_name == 'carbohydrate':
                suggested_recipes = Recipe.objects.order_by('-total_carbohydrates')[:5]
                message = f"炭水化物が約{main_deficit[1]:.0f}g不足しています。エネルギー源となる食品をおすすめします。"
            else:
                suggested_recipes = Recipe.objects.order_by('-total_calories')[:5]
                message = f"カロリーが約{main_deficit[1]:.0f}kcal不足しています。"

        serializer = RecipeSerializer(suggested_recipes, many=True)
        
        return Response({
            "message": message,
            "suggestions": serializer.data,
            "optimization_summary": {
                "current_intake": current_intake,
                "targets": targets,
                "deficits": deficits
            },
            "is_optimized": False,
            "note": "高度な最適化は利用できませんでしたが、栄養不足に基づいて提案を行いました。"
        })


class OptimizedPlanView(APIView):
    """
    1日全体の最適化された食事プランを提案
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            profile = user.profile
        except (UserProfile.DoesNotExist, AttributeError):
            return Response({"error": "ユーザープロフィールが見つかりません。"}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # 目標値を取得
        targets = {
            'protein': profile.target_protein or 70,
            'fat': profile.target_fat or 60,
            'carbohydrate': profile.target_carbohydrate or 250,
            'calories': getattr(profile, 'target_calories', None) or 2000,
        }

        # 最適化レベルを取得（クエリパラメータから）
        optimization_level = request.GET.get('level', 'standard')
        
        try:
            optimizer = NutritionOptimizer()
            
            # 最適化制約を設定
            constraints = {}
            if optimization_level == 'strict':
                constraints['min_meals'] = 3  # 最低3品目
                constraints['max_sodium'] = 2300  # ナトリウム制限
            elif optimization_level == 'flexible':
                # より柔軟な制約
                pass
            
            result = optimizer.optimize_daily_meal(
                targets=targets,
                current_intake=None,  # 1日全体の計画なので現在摂取量は考慮しない
                constraints=constraints
            )

            if result[0] is not None:
                meal_data = result[0]
                
                # レシピをシリアライズ
                recipes = [item['recipe'] for item in meal_data['meal_plan']]
                serializer = RecipeSerializer(recipes, many=True)
                
                # 推奨量を追加
                plan_data = []
                for i, recipe_data in enumerate(serializer.data):
                    recipe_data['recommended_quantity'] = meal_data['meal_plan'][i]['quantity']
                    recipe_data['nutrition_contribution'] = meal_data['meal_plan'][i].get('nutrition_contribution', {})
                    plan_data.append(recipe_data)

                return Response({
                    "message": result[1],
                    "plan": plan_data,
                    "optimization_summary": {
                        "total_nutrition": meal_data.get('total_nutrition', {}),
                        "achievement_rates": meal_data.get('achievement_rates', {}),
                        "targets": targets
                    },
                    "optimization_level": optimization_level,
                    "total_estimated_cost": sum(
                        recipe.total_calories * item['quantity'] * 0.01  # 仮のコスト計算
                        for recipe, item in zip(recipes, meal_data['meal_plan'])
                    )
                })
            else:
                return Response({"error": result[1]}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Optimization plan error: {e}")
            return Response({
                "error": f"最適化プランの生成に失敗しました: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DinnerSuggestionView(APIView):
    """
    朝食・昼食を考慮した夕食提案（線形計画法ベース）
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            profile = user.profile
        except (UserProfile.DoesNotExist, AttributeError):
            return Response({"error": "ユーザープロフィールが見つかりません。"}, 
                          status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()

        # 1日の目標値
        daily_targets = {
            'protein': profile.target_protein or 70,
            'fat': profile.target_fat or 60,
            'carbohydrate': profile.target_carbohydrate or 250,
            'calories': getattr(profile, 'target_calories', None) or 2000,
        }

        # 朝食・昼食の摂取量を計算
        morning_intake = MealItem.objects.filter(
            meal__user=user,
            meal__recorded_at__date=today,
            meal__meal_type__in=['breakfast', 'lunch']
        ).aggregate(
            protein=Coalesce(Sum('protein'), 0.0, output_field=FloatField()),
            fat=Coalesce(Sum('fat'), 0.0, output_field=FloatField()),
            carbohydrates=Coalesce(Sum('carbohydrates'), 0.0, output_field=FloatField()),
            calories=Coalesce(Sum('calories'), 0.0, output_field=FloatField())
        )

        current_intake = {
            'protein': morning_intake['protein'],
            'fat': morning_intake['fat'],
            'carbohydrate': morning_intake['carbohydrates'],
            'calories': morning_intake['calories']
        }

        # 夕食で必要な栄養素を計算
        dinner_targets = {
            key: max(0, daily_targets[key] - current_intake[key])
            for key in daily_targets.keys()
        }

        try:
            optimizer = NutritionOptimizer()
            
            # 夕食専用の制約（軽めに設定）
            dinner_constraints = {
                'max_calories': dinner_targets['calories'] * 1.1,  # 少し余裕を持たせる
            }
            
            result = optimizer.optimize_daily_meal(
                targets=dinner_targets,
                current_intake=None,
                constraints=dinner_constraints
            )

            if result[0] is not None:
                meal_plan = result[0]['meal_plan']
                recipes = [item['recipe'] for item in meal_plan]
                serializer = RecipeSerializer(recipes, many=True)
                
                # 推奨量を追加
                dinner_suggestions = []
                for i, recipe_data in enumerate(serializer.data):
                    recipe_data['recommended_quantity'] = meal_plan[i]['quantity']
                    dinner_suggestions.append(recipe_data)

                return Response({
                    "message": result[1],
                    "suggestions": dinner_suggestions,
                    "dinner_analysis": {
                        "remaining_targets": dinner_targets,
                        "current_intake": current_intake,
                        "daily_targets": daily_targets,
                        "achievement_rate": {
                            key: (current_intake[key] / daily_targets[key] * 100) 
                            if daily_targets[key] > 0 else 100
                            for key in daily_targets.keys()
                        }
                    },
                    "optimization_summary": result[0].get('total_nutrition', {}),
                    "is_optimized": True
                })
            else:
                # フォールバック：シンプルな夕食提案
                return self._simple_dinner_fallback(dinner_targets, current_intake, daily_targets)
                
        except Exception as e:
            logger.error(f"Dinner optimization error: {e}")
            return self._simple_dinner_fallback(dinner_targets, current_intake, daily_targets)

    def _simple_dinner_fallback(self, dinner_targets, current_intake, daily_targets):
        """夕食最適化失敗時のシンプルなフォールバック"""
        # 最も不足している栄養素を特定
        max_deficit_nutrient = max(dinner_targets.items(), key=lambda x: x[1])
        nutrient_name, deficit_amount = max_deficit_nutrient
        
        if deficit_amount > 10:  # 10以上不足している場合
            if nutrient_name == 'protein':
                suggested_recipes = Recipe.objects.annotate(
                    diff=Abs(F('total_protein') - deficit_amount)
                ).order_by('diff')[:3]
                message = f"夕食でタンパク質を約{deficit_amount:.0f}g摂取することをおすすめします。"
            elif nutrient_name == 'carbohydrate':
                suggested_recipes = Recipe.objects.annotate(
                    diff=Abs(F('total_carbohydrates') - deficit_amount)
                ).order_by('diff')[:3]
                message = f"夕食で炭水化物を約{deficit_amount:.0f}g摂取することをおすすめします。"
            elif nutrient_name == 'fat':
                suggested_recipes = Recipe.objects.annotate(
                    diff=Abs(F('total_fat') - deficit_amount)
                ).order_by('diff')[:3]
                message = f"夕食で脂質を約{deficit_amount:.0f}g摂取することをおすすめします。"
            else:  # calories
                suggested_recipes = Recipe.objects.order_by('total_calories')[:3]
                message = f"夕食では軽めの{deficit_amount:.0f}kcal程度がおすすめです。"
        else:
            # 大きな不足がない場合
            suggested_recipes = Recipe.objects.order_by('total_calories')[:3]
            message = "今日の栄養は順調です！軽めの夕食はいかがですか？"

        serializer = RecipeSerializer(suggested_recipes, many=True)
        return Response({
            "message": message,
            "suggestions": serializer.data,
            "dinner_analysis": {
                "remaining_targets": dinner_targets,
                "current_intake": current_intake,
                "daily_targets": daily_targets
            },
            "is_optimized": False,
            "note": "シンプルな栄養分析に基づく提案です。"
        })