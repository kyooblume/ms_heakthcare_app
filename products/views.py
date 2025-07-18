# products/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import requests # 外部APIリクエスト用
from .models import ProductNutrition
from .serializers import ProductNutritionSerializer
from recipes.models import Recipe 


class ProductLookupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, barcode):
        # 1. まず自分たちのDB（キャッシュ）に情報がないか探す
        try:
            product = ProductNutrition.objects.get(barcode=barcode)
            serializer = ProductNutritionSerializer(product)
            return Response(serializer.data)
        except ProductNutrition.DoesNotExist:
            # 2. キャッシュになければ、外部APIに問い合わせる
            pass


# 2. 次に、バーコードが「数字」なら、自分たちの「レシピDB」を探す
        if barcode.isdigit(): # バーコードが数字だけで構成されているかチェック
            try:
                recipe_id = int(barcode) # 文字列を、数字に変換
                recipe = Recipe.objects.get(id=recipe_id)
                
                # レシピが見つかったら、商品キャッシュとして新しく作成
                new_product = ProductNutrition.objects.create(
                    barcode=barcode,
                    product_name=recipe.title,
                    calories=recipe.total_calories,
                    protein=recipe.total_protein,
                    fat=recipe.total_fat,
                    carbohydrates=recipe.total_carbohydrates,
                    image_url=recipe.image_url,
                    source='internal_recipe'
                )
                serializer = ProductNutritionSerializer(new_product)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except (Recipe.DoesNotExist, ValueError):
                # レシピが見つからないか、数字への変換に失敗したら、次のステップへ
                pass
        # --- ★ここまでが、新しいロジックです ---

        # Open Food Facts APIのエンドポイント
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
            data = response.json()

            if data.get("status") == 1:
                # 商品が見つかった場合
                product_data = data.get("product")
                nutriments = product_data.get("nutriments", {})

                # 必要な情報を抽出して、自分たちのDBに保存（キャッシュ）
                new_product = ProductNutrition.objects.create(
                    barcode=barcode,
                    product_name=product_data.get("product_name_ja") or product_data.get("product_name"),
                    calories=nutriments.get("energy-kcal_100g"),
                    protein=nutriments.get("proteins_100g"),
                    fat=nutriments.get("fat_100g"),
                    carbohydrates=nutriments.get("carbohydrates_100g"),
                    image_url=product_data.get("image_url")
                )
                serializer = ProductNutritionSerializer(new_product)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # 商品が見つからなかった場合
                return Response({"error": "商品が見つかりませんでした。"}, status=status.HTTP_404_NOT_FOUND)

        except requests.exceptions.RequestException as e:
            # 外部APIへの接続エラーなど
            return Response({"error": f"外部APIへの接続に失敗しました: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)