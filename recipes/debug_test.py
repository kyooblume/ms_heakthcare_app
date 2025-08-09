# recipes/debug_test.py
# このファイルをrecipesアプリのディレクトリに作成し、Django shellで実行してテストできます

from django.contrib.auth.models import User
from accounts.models import UserProfile
from .models import Recipe, Ingredient
from meals.models import Meal, MealItem
from django.utils import timezone

def create_test_data():
    """テスト用のデータを作成する関数"""
    
    # 1. テストユーザーを作成
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # 2. ユーザープロフィールを作成
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'target_protein': 80.0,
            'target_fat': 65.0,
            'target_carbohydrate': 300.0,
            'nutrition_priority': 'balance'
        }
    )
    
    # 3. テスト用レシピを作成
    recipes_data = [
        {
            'title': '鶏胸肉のグリル',
            'description': 'ヘルシーな高タンパク料理',
            'total_calories': 200,
            'total_protein': 35,
            'total_fat': 5,
            'total_carbohydrates': 2
        },
        {
            'title': '玄米ご飯',
            'description': '良質な炭水化物源',
            'total_calories': 150,
            'total_protein': 3,
            'total_fat': 1,
            'total_carbohydrates': 30
        },
        {
            'title': '野菜サラダ',
            'description': 'ビタミン・ミネラル豊富',
            'total_calories': 50,
            'total_protein': 2,
            'total_fat': 8,
            'total_carbohydrates': 10
        },
        {
            'title': 'サーモンステーキ',
            'description': '良質な脂質とタンパク質',
            'total_calories': 250,
            'total_protein': 25,
            'total_fat': 15,
            'total_carbohydrates': 0
        },
        {
            'title': 'アボカドトースト',
            'description': '健康的な脂質を含む朝食',
            'total_calories': 180,
            'total_protein': 6,
            'total_fat': 12,
            'total_carbohydrates': 15
        }
    ]
    
    for recipe_data in recipes_data:
        recipe, created = Recipe.objects.get_or_create(
            title=recipe_data['title'],
            defaults=recipe_data
        )
        print(f"レシピ作成: {recipe.title} ({'新規' if created else '既存'})")
    
    # 4. 今日の食事記録を作成（朝食と昼食のみ）
    today = timezone.now().date()
    
    # 朝食
    breakfast, created = Meal.objects.get_or_create(
        user=user,
        meal_type='breakfast',
        recorded_at=timezone.now().replace(hour=8, minute=0, second=0, microsecond=0),
        defaults={'notes': 'テスト朝食'}
    )
    
    # 朝食のアイテム
    MealItem.objects.get_or_create(
        meal=breakfast,
        name='トースト',
        defaults={
            'calories': 150,
            'protein': 5,
            'fat': 3,
            'carbohydrates': 25
        }
    )
    
    # 昼食
    lunch, created = Meal.objects.get_or_create(
        user=user,
        meal_type='lunch',
        recorded_at=timezone.now().replace(hour=12, minute=0, second=0, microsecond=0),
        defaults={'notes': 'テスト昼食'}
    )
    
    # 昼食のアイテム
    MealItem.objects.get_or_create(
        meal=lunch,
        name='チキンサラダ',
        defaults={
            'calories': 200,
            'protein': 20,
            'fat': 8,
            'carbohydrates': 10
        }
    )
    
    print("テストデータの作成が完了しました！")
    print(f"ユーザー: {user.username}")
    print(f"プロフィール目標: P={profile.target_protein}g, F={profile.target_fat}g, C={profile.target_carbohydrate}g")
    print(f"レシピ数: {Recipe.objects.count()}")
    print(f"今日の食事記録: {Meal.objects.filter(user=user, recorded_at__date=today).count()}件")

def test_recipe_suggestions():
    """レシピ提案のテスト"""
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    user = User.objects.get(username='testuser')
    
    # JWTトークンを生成
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # レシピ提案APIをテスト
    response = client.get('/api/recipes/suggestions/')
    print(f"レスポンスステータス: {response.status_code}")
    print(f"レスポンスデータ: {response.data}")
    
    return response

if __name__ == "__main__":
    print("テストデータを作成中...")
    create_test_data()
    print("\nレシピ提案APIをテスト中...")
    test_recipe_suggestions()