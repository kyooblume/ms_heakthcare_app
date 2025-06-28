# meals/views.py
from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.utils import timezone
from django.db.models import Sum, Avg, Max, Min

from .models import MealLog, FoodMaster, Meal, MealItem
from .serializers import MealLogSerializer, FoodMasterSerializer, MealSerializer, MealItemSerializer


class FoodMasterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    食品マスターデータを名前で検索・閲覧するための読み取り専用APIビュー。
    """
    queryset = FoodMaster.objects.all().order_by('id')
    serializer_class = FoodMasterSerializer
    permission_classes = [IsAuthenticated]
    
    # 検索機能
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class MealLogViewSet(viewsets.ModelViewSet):
    """
    食事記録のCRUD操作を行うためのAPIビューセット。
    認証されたユーザーは、自身の食事記録のみを操作できる。
    """
    serializer_class = MealLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """現在のリクエストユーザーに紐づく食事記録のみを返す"""
        return MealLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """新しい食事記録を作成する際に、現在のユーザーを自動的に紐付ける"""
        serializer.save(user=self.request.user)


class DailyNutritionReportView(APIView):
    """日次栄養レポートを取得するビュー"""
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        try:
            # URLから受け取った日付文字列を日付オブジェクトに変換
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "無効な日付形式です。YYYY-MM-DDで指定してください。"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        
        # ユーザープロファイルが存在するかチェック
        try:
            profile = user.profile
        except AttributeError:
            # プロファイルが存在しない場合のデフォルト値
            target_calories = 2000
            target_protein = 60
        else:
            target_calories = getattr(profile, 'target_calories', 2000)
            target_protein = getattr(profile, 'target_protein', 60)

        # その日の食事記録を取得
        meal_logs = MealLog.objects.filter(user=user, eaten_at__date=target_date)

        # 栄養素の合計を計算
        actual_calories = 0
        actual_protein = 0
        
        for log in meal_logs:
            for component in log.components.all():
                # 食べた量(g)に応じて栄養素を計算
                ratio = component.quantity / 100.0
                actual_calories += component.food.calories_per_100g * ratio
                actual_protein += component.food.protein_per_100g * ratio

        # レスポンスデータを作成
        response_data = {
            "date": target_date,
            "summary": {
                "calories": {
                    "target": target_calories, 
                    "actual": round(actual_calories), 
                    "balance": round(actual_calories - target_calories)
                },
                "protein": {
                    "target": target_protein, 
                    "actual": round(actual_protein, 1), 
                    "balance": round(actual_protein - target_protein, 1)
                },
            }
        }
        return Response(response_data)


class AddMealFromBarcodeView(APIView):
    """バーコードと量から食事記録を作成するビュー"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        barcode = request.data.get('barcode')
        quantity = float(request.data.get('quantity', 100.0))
        meal_type = request.data.get('meal_type', 'snack')
        
        if not barcode:
            return Response(
                {"error": "バーコードが指定されていません。"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # ProductNutritionモデルをインポートして使用
        try:
            from products.models import ProductNutrition
            product = ProductNutrition.objects.get(barcode=barcode)
        except ImportError:
            return Response(
                {"error": "商品データベースモジュールが見つかりません。"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ProductNutrition.DoesNotExist:
            return Response(
                {"error": "その商品はデータベースに登録されていません。先にバーコード検索を行ってください。"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # 栄養素を計算
        calories = (product.calories / 100) * quantity if product.calories else None
        protein = (product.protein / 100) * quantity if product.protein else None
        fat = (product.fat / 100) * quantity if product.fat else None
        carbohydrates = (product.carbohydrates / 100) * quantity if product.carbohydrates else None

        # 今日の食事を取得または作成
        today = timezone.now().date()
        meal, created = Meal.objects.get_or_create(
            user=request.user,
            meal_type=meal_type,
            recorded_at__date=today,
            defaults={'recorded_at': timezone.now()}
        )
        
        # 食事アイテムを作成
        MealItem.objects.create(
            meal=meal,
            food_name=product.product_name,
            calories=calories,
            protein=protein,
            fat=fat,
            carbohydrates=carbohydrates,
            quantity=quantity,
            unit='g'
        )

        serializer = MealSerializer(meal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)