# recipes/optimization.py - 改良版

import numpy as np
from scipy.optimize import linprog
from .models import Recipe
import logging

logger = logging.getLogger(__name__)

class NutritionOptimizer:
    """
    線形計画法を用いた栄養最適化システム
    """
    
    def __init__(self):
        self.recipes = None
        self.nutrition_matrix = None
        self.recipe_costs = None  # カロリーまたはコスト
        
    def load_recipes(self):
        """レシピデータを読み込み、行列形式に変換"""
        self.recipes = list(Recipe.objects.all())
        if not self.recipes:
            raise ValueError("レシピが登録されていません")
        
        # 栄養素行列の作成 [タンパク質, 脂質, 炭水化物, カロリー, 食物繊維, ナトリウム...]
        self.nutrition_matrix = np.array([
            [
                recipe.total_protein,
                recipe.total_fat, 
                recipe.total_carbohydrates,
                recipe.total_calories,
                getattr(recipe, 'total_fiber', 0),      # 食物繊維（もしフィールドがあれば）
                getattr(recipe, 'total_sodium', 0),     # ナトリウム
                getattr(recipe, 'total_sugar', 0),      # 糖質
                getattr(recipe, 'total_calcium', 0),    # カルシウム
                getattr(recipe, 'total_iron', 0),       # 鉄分
                getattr(recipe, 'total_vitamin_c', 0),  # ビタミンC
            ]
            for recipe in self.recipes
        ])
        
        # コスト関数（最小化対象）- ここではカロリーを使用
        self.recipe_costs = self.nutrition_matrix[:, 3]  # カロリー列
        
        logger.info(f"読み込み完了: {len(self.recipes)}件のレシピ")
        
    def optimize_daily_meal(self, targets, current_intake=None, constraints=None):
        """
        1日の食事を最適化
        
        Args:
            targets (dict): 目標栄養素 {'protein': 80, 'fat': 60, 'carbohydrate': 250, 'calories': 2000}
            current_intake (dict): 現在の摂取量（任意）
            constraints (dict): 追加制約（任意）
        
        Returns:
            tuple: (最適化結果, メッセージ)
        """
        if self.recipes is None:
            self.load_recipes()
            
        # 現在の摂取量を考慮して残り目標を計算
        remaining_targets = self._calculate_remaining_targets(targets, current_intake)
        
        # 制約条件の設定
        constraints_result = self._setup_constraints(remaining_targets, constraints)
        
        if constraints_result is None:
            return None, "制約条件の設定に失敗しました"
            
        A_ub, b_ub, A_eq, b_eq, bounds = constraints_result
        
        try:
            # 線形計画問題を解く
            result = linprog(
                c=self.recipe_costs,  # 最小化対象（カロリー）
                A_ub=A_ub,           # 不等式制約の係数行列
                b_ub=b_ub,           # 不等式制約の右辺
                A_eq=A_eq,           # 等式制約の係数行列（任意）
                b_eq=b_eq,           # 等式制約の右辺（任意）
                bounds=bounds,        # 変数の境界
                method='highs',       # 高性能ソルバー
                options={'disp': False}
            )
            
            if result.success:
                return self._process_optimization_result(result, remaining_targets)
            else:
                return self._handle_infeasible_solution(remaining_targets)
                
        except Exception as e:
            logger.error(f"最適化エラー: {e}")
            return None, f"最適化処理中にエラーが発生しました: {str(e)}"
    
    def _calculate_remaining_targets(self, targets, current_intake):
        """残りの目標栄養素を計算"""
        if current_intake is None:
            return targets
            
        return {
            'protein': max(0, targets.get('protein', 0) - current_intake.get('protein', 0)),
            'fat': max(0, targets.get('fat', 0) - current_intake.get('fat', 0)),
            'carbohydrate': max(0, targets.get('carbohydrate', 0) - current_intake.get('carbohydrate', 0)),
            'calories': max(0, targets.get('calories', 2000) - current_intake.get('calories', 0))
        }
    
    def _setup_constraints(self, targets, additional_constraints=None):
        """制約条件を設定"""
        try:
            # 基本的な栄養素制約
            # A_ub @ x <= b_ub の形式で設定
            
            constraints_list = []
            bounds_list = []
            
            # 1. 栄養素の最小値制約 (-A @ x <= -b で A @ x >= b を表現)
            if targets.get('protein', 0) > 0:
                constraints_list.append((-self.nutrition_matrix[:, 0], -targets['protein']))  # タンパク質
            
            if targets.get('fat', 0) > 0:
                constraints_list.append((-self.nutrition_matrix[:, 1], -targets['fat']))      # 脂質
                
            if targets.get('carbohydrate', 0) > 0:
                constraints_list.append((-self.nutrition_matrix[:, 2], -targets['carbohydrate']))  # 炭水化物
            
            # 2. カロリーの上限制約（過剰摂取防止）
            max_calories = targets.get('calories', 2000) * 1.2  # 20%のバッファ
            constraints_list.append((self.nutrition_matrix[:, 3], max_calories))
            
            # 3. 各レシピの量の制約（0以上、適切な上限以下）
            n_recipes = len(self.recipes)
            for i in range(n_recipes):
                bounds_list.append((0, 2.0))  # 0人前以上、2人前以下
            
            # 4. 追加制約の処理
            if additional_constraints:
                # 例: 特定の栄養素の上限
                if 'max_sodium' in additional_constraints:
                    sodium_idx = 5  # ナトリウムのインデックス
                    constraints_list.append((self.nutrition_matrix[:, sodium_idx], additional_constraints['max_sodium']))
                
                # 例: 最低食事数制約
                if 'min_meals' in additional_constraints:
                    # 少なくともN品目は選ぶ（各レシピが0.1人前以上の場合をカウント）
                    # これは線形制約では表現が困難なので、後処理で調整
                    pass
            
            # 制約行列の構築
            if constraints_list:
                A_ub = np.vstack([constraint[0] for constraint in constraints_list])
                b_ub = np.array([constraint[1] for constraint in constraints_list])
            else:
                A_ub = None
                b_ub = None
            
            # 等式制約（現在は使用しない）
            A_eq = None
            b_eq = None
            
            # 境界条件
            bounds = bounds_list if bounds_list else None
            
            return A_ub, b_ub, A_eq, b_eq, bounds
            
        except Exception as e:
            logger.error(f"制約設定エラー: {e}")
            return None
    
    def _process_optimization_result(self, result, targets):
        """最適化結果を処理"""
        meal_plan = []
        total_nutrition = np.zeros(10)  # 10種類の栄養素
        
        for i, quantity in enumerate(result.x):
            if quantity > 0.05:  # 0.05人前以上のレシピを採用
                recipe = self.recipes[i]
                rounded_quantity = round(quantity, 2)
                
                meal_plan.append({
                    'recipe': recipe,
                    'quantity': rounded_quantity,
                    'nutrition_contribution': {
                        'protein': recipe.total_protein * rounded_quantity,
                        'fat': recipe.total_fat * rounded_quantity,
                        'carbohydrate': recipe.total_carbohydrates * rounded_quantity,
                        'calories': recipe.total_calories * rounded_quantity
                    }
                })
                
                # 合計栄養素を計算
                total_nutrition += self.nutrition_matrix[i] * rounded_quantity
        
        # 達成率を計算
        achievement_rates = {}
        for nutrient, target_value in targets.items():
            if target_value > 0:
                if nutrient == 'protein':
                    actual = total_nutrition[0]
                elif nutrient == 'fat':
                    actual = total_nutrition[1]
                elif nutrient == 'carbohydrate':
                    actual = total_nutrition[2]
                elif nutrient == 'calories':
                    actual = total_nutrition[3]
                else:
                    continue
                    
                achievement_rates[nutrient] = (actual / target_value) * 100
        
        # メッセージ生成
        message = self._generate_optimization_message(achievement_rates, len(meal_plan))
        
        return {
            'meal_plan': meal_plan,
            'total_nutrition': {
                'protein': round(total_nutrition[0], 1),
                'fat': round(total_nutrition[1], 1),
                'carbohydrate': round(total_nutrition[2], 1),
                'calories': round(total_nutrition[3], 1)
            },
            'achievement_rates': achievement_rates,
            'optimization_status': result.message
        }, message
    
    def _handle_infeasible_solution(self, targets):
        """解が見つからない場合の処理"""
        # 制約を緩和したフォールバック解を提案
        fallback_recipes = []
        
        # 不足栄養素に対して単純な優先順位付けで選択
        sorted_nutrients = sorted(targets.items(), key=lambda x: x[1], reverse=True)
        
        for nutrient, target_value in sorted_nutrients[:3]:  # 上位3つの栄養素
            if target_value <= 0:
                continue
                
            # 該当栄養素が豊富なレシピを選択
            if nutrient == 'protein':
                best_recipes = sorted(self.recipes, key=lambda r: r.total_protein, reverse=True)[:2]
            elif nutrient == 'fat':
                best_recipes = sorted(self.recipes, key=lambda r: r.total_fat, reverse=True)[:2]
            elif nutrient == 'carbohydrate':
                best_recipes = sorted(self.recipes, key=lambda r: r.total_carbohydrates, reverse=True)[:2]
            else:
                continue
            
            for recipe in best_recipes:
                if recipe not in [item['recipe'] for item in fallback_recipes]:
                    fallback_recipes.append({
                        'recipe': recipe,
                        'quantity': 1.0,
                        'reason': f'{nutrient}補給のため'
                    })
        
        return {
            'meal_plan': fallback_recipes,
            'is_fallback': True
        }, "完全な最適解が見つからなかったため、代替案を提案します。"
    
    def _generate_optimization_message(self, achievement_rates, meal_count):
        """最適化結果に基づいてメッセージを生成"""
        avg_achievement = sum(achievement_rates.values()) / len(achievement_rates)
        
        if avg_achievement >= 95:
            return f"素晴らしい！{meal_count}品の料理で栄養バランスが完璧に近づきます。"
        elif avg_achievement >= 80:
            return f"{meal_count}品の料理で栄養目標の約{avg_achievement:.0f}%を達成できます。"
        elif avg_achievement >= 60:
            return f"{meal_count}品の料理で基本的な栄養は確保できますが、さらなる工夫が必要かもしれません。"
        else:
            return "現在のレシピデータでは目標達成が困難です。レシピの追加を検討してください。"


def optimize_meal_plan(targets, current_intake=None, optimization_goal='balanced'):
    """
    公開API関数 - 既存のコードとの互換性を保つ
    
    Args:
        targets (dict): 栄養目標
        current_intake (dict): 現在の摂取量
        optimization_goal (str): 最適化目標 ('balanced', 'low_calorie', 'high_protein')
    """
    try:
        optimizer = NutritionOptimizer()
        
        # 最適化目標に応じて制約を調整
        additional_constraints = {}
        if optimization_goal == 'low_calorie':
            # カロリー制限を厳しくする
            targets['calories'] = min(targets.get('calories', 2000), 1600)
        elif optimization_goal == 'high_protein':
            # タンパク質目標を引き上げ
            targets['protein'] = targets.get('protein', 70) * 1.2
        
        result = optimizer.optimize_daily_meal(
            targets=targets,
            current_intake=current_intake,
            constraints=additional_constraints
        )
        
        if result[0] is None:
            return None, result[1]
        
        # 既存のフォーマットに変換
        meal_plan = []
        for item in result[0]['meal_plan']:
            meal_plan.append({
                'recipe': item['recipe'],
                'quantity': item['quantity']
            })
        
        return meal_plan, result[1]
        
    except Exception as e:
        logger.error(f"Meal optimization error: {e}")
        return None, f"最適化に失敗しました: {str(e)}"