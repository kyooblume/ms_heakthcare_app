# recipes/optimization.py

import numpy as np
from scipy.optimize import linprog
from .models import Recipe

def optimize_meal_plan(targets):
    """
    線形計画法を用いて、栄養目標を達成する最適なレシピの組み合わせを見つけ出す。
    """
    # 1. データベースから全てのレシピの栄養素データを取得
    recipes = list(Recipe.objects.all())
    if not recipes:
        return None, "レシピが登録されていません。"

    # 各レシピの栄養素を行列として整理
    # (タンパク質, 脂質, 炭水化物, カロリー)
    nutrients = np.array([
        [r.total_protein, r.total_fat, r.total_carbohydrates, r.total_calories]
        for r in recipes
    ])

    # 2. 線形計画法の問題を設定
    # 目的: 目標との誤差を最小化したいが、ここでは簡略化のため「カロリー」を目標に近づける
    # c: 各レシピのカロリー（これを最小化または最大化の対象にする）
    c = nutrients[:, 3]

    # 制約条件: 各栄養素が目標値を満たすようにする
    # A_ub @ x <= b_ub  (「以下」の制約)
    # A_eq @ x == b_eq  (「等しい」の制約)
    
    # 今回は、「各栄養素が目標値以上であること」を制約とする
    # -A_ub @ x >= -b_ub
    A_ub = -np.array([
        nutrients[:, 0], # タンパク質
        nutrients[:, 1], # 脂質
        nutrients[:, 2], # 炭水化物
    ])
    
    b_ub = -np.array([
        targets['protein'],
        targets['fat'],
        targets['carbohydrate'],
    ])
    
    # 各レシピの量は0人前以上、2人前以下とする (食べ過ぎ防止)
    x_bounds = (0, 2)

    # 3. 線形計画問題を解く！
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=x_bounds, method='highs')

    if result.success:
        # 4. 結果を解釈する
        plan = []
        for i, quantity in enumerate(result.x):
            # 0.1人前以上食べるレシピだけをリストアップ
            if quantity > 0.1:
                plan.append({
                    "recipe": recipes[i],
                    "quantity": round(quantity, 2) # 小数点第2位まで
                })
        return plan, "最適な献立プランが見つかりました！"
    else:
        return None, "条件に合う献立プランが見つかりませんでした。制約が厳しすぎる可能性があります。"