# meals/management/commands/import_food_data.py
import csv
from django.core.management.base import BaseCommand
from meals.models import FoodMaster

class Command(BaseCommand):
    help = '新しいシンプルな列名を持つCSVをインポートします'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='インポートするCSVファイルのパス')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        self.stdout.write(self.style.SUCCESS(f'"{csv_file_path}" からインポートを開始します...'))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        food_name = row.get('食品名', '').strip()
                        if not food_name:
                            continue

                        FoodMaster.objects.update_or_create(
                            name=food_name,
                            defaults={
                                'calories_per_100g': int(row.get('エネルギー') or 0),
                                'water_g': float(row.get('水分') or 0),
                                'protein_per_100g': float(row.get('たんぱく質') or 0),
                                'fat_per_100g': float(row.get('脂質') or 0),
                                'carbohydrate_per_100g': float(row.get('炭水化物') or 0),
                                'sodium_mg': int(row.get('ナトリウム') or 0),
                                'potassium_mg': int(row.get('カリウム') or 0),
                                'calcium_mg': int(row.get('カルシウム') or 0),
                                'magnesium_mg': int(row.get('マグネシウム') or 0),
                                'phosphorus_mg': int(row.get('リン') or 0),
                                'iron_mg': float(row.get('鉄') or 0),
                                'zinc_mg': float(row.get('亜鉛') or 0),
                                'copper_mg': float(row.get('銅') or 0),
                                'manganese_mg': float(row.get('マンガン') or 0),
                                'iodine_mcg': int(row.get('ヨウ素') or 0),
                                'selenium_mcg': int(row.get('セレン') or 0),
                                'chromium_mcg': int(row.get('クロム') or 0),
                                'molybdenum_mcg': int(row.get('モリブデン') or 0),
                                'vitamin_a_mcg': int(row.get('ビタミンA') or 0),
                                'vitamin_d_mcg': float(row.get('ビタミンD') or 0),
                                'vitamin_e_mg': float(row.get('ビタミンE') or 0),
                                'vitamin_k_mcg': int(row.get('ビタミンK') or 0),
                                'vitamin_b1_mg': float(row.get('ビタミンB1') or 0),
                                'vitamin_b2_mg': float(row.get('ビタミンB2') or 0),
                                'niacin_mg': float(row.get('ナイアシン当量') or 0),
                                'vitamin_b6_mg': float(row.get('ビタミンB6') or 0),
                                'vitamin_b12_mcg': float(row.get('ビタミンB12') or 0),
                                'folate_mcg': int(row.get('葉酸') or 0),
                                'pantothenic_acid_mg': float(row.get('パントテン酸') or 0),
                                'biotin_mcg': float(row.get('ビオチン') or 0),
                                'vitamin_c_mg': float(row.get('ビタミンC') or 0),
                                'alcohol_g': float(row.get('アルコール') or 0),
                                'salt_equivalent_per_100g': float(row.get('食塩相当量') or 0),
                            }
                        )
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f'エラー: 行の処理中に問題 - {e} | データ: {row}'))
                        continue
            self.stdout.write(self.style.SUCCESS('インポートが完了しました。'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'予期せぬエラーが発生しました: {e}'))