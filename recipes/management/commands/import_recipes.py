## recipes/management/commands/import_recipes.py

import csv
from django.core.management.base import BaseCommand
from recipes.models import Recipe, Ingredient

class Command(BaseCommand):
    help = 'CSVファイルからレシピと材料を一括でインポートします'

    def handle(self, *args, **options):
        # --- まず、既存のデータを全て削除（重複を防ぐため） ---
        self.stdout.write('既存のレシピデータを削除しています...')
        Ingredient.objects.all().delete()
        Recipe.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('既存のレシピデータを削除しました。'))

        # --- レシピCSVファイルのインポート ---
        recipe_csv_path = 'recipes.csv' # プロジェクトのルートディレクトリに置く
        ingredient_csv_path = 'ingredients.csv'
        recipe_map = {} # CSVのIDとDBのIDを紐付けるため

        try:
            with open(recipe_csv_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # 空の値をNoneに変換
                    for key, value in row.items():
                        if value == '':
                            row[key] = None
                    
                    # --- ★ここを修正 ---
                    # CSVからidを読み込み、新しいDBのidと紐付ける
                    csv_id = row['id']
                    recipe = Recipe.objects.create(
                        title=row['title'],
                        description=row['description'],
                        instructions=row['instructions'],
                        image_url=row['image_url'],
                        total_calories=row['total_calories'],
                        total_protein=row['total_protein'],
                        total_fat=row['total_fat'],
                        total_carbohydrates=row['total_carbohydrates']
                    )
                    recipe_map[csv_id] = recipe.id
            self.stdout.write(self.style.SUCCESS(f'{recipe_csv_path} から {len(recipe_map)} 件のレシピをインポートしました。'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'{recipe_csv_path} が見つかりません。'))
            return
        except KeyError:
            self.stdout.write(self.style.ERROR(f'エラー: {recipe_csv_path} に "id" 列が見つかりません。ヘッダー行を確認してください。'))
            return

        try:
            with open(ingredient_csv_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                ingredients_to_create = []
                for row in reader:
                    csv_recipe_id = row['recipe_id']
                    db_recipe_id = recipe_map.get(csv_recipe_id)
                    
                    if db_recipe_id:
                        ingredient = Ingredient(
                            recipe_id=db_recipe_id,
                            name=row['name'],
                            quantity=row['quantity']
                        )
                        ingredients_to_create.append(ingredient)

                Ingredient.objects.bulk_create(ingredients_to_create)
            self.stdout.write(self.style.SUCCESS(f'{ingredient_csv_path} から {len(ingredients_to_create)} 件の材料をインポートしました。'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'{ingredient_csv_path} が見つかりません。'))