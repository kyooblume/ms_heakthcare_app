# health_records/management/commands/seed_dummy_data.py
#ダミーデータを登録するためのDjango管理コマンド
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from health_records.models import HealthRecord
from meals.models import Meal, MealItem

class Command(BaseCommand):
    help = '指定されたユーザーのダミー健康データをCSVから一括で登録します'

    def add_arguments(self, parser):
        # コマンド実行時にユーザー名を指定できるようにする
        parser.add_argument('username', type=str, help='データを登録するユーザー名')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'ユーザー "{username}" が見つかりません。'))
            return

        csv_path = 'dummy_data.csv' # プロジェクトのルートディレクトリに置く
        self.stdout.write(f'{csv_path} から {username} のデータを登録します...')

        try:
            with open(csv_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date = datetime.strptime(row['date'], '%Y-%m-%d').date()

                    # --- 歩数データの登録 ---
                    if row.get('steps'):
                        HealthRecord.objects.update_or_create(
                            user=user,
                            record_type='steps',
                            recorded_at__date=date,
                            defaults={'value_numeric': float(row['steps'])}
                        )
                    
                    # --- 睡眠時間データの登録 ---
                    if row.get('sleep_hours'):
                        HealthRecord.objects.update_or_create(
                            user=user,
                            record_type='sleep',
                            recorded_at__date=date,
                            defaults={'value_numeric': float(row['sleep_hours'])}
                        )

                    # --- 食事データの登録 ---
                    if row.get('meal_barcode'):
                        # 食事は簡略化のため、ランチのスナックとして固定で登録
                        meal, created = Meal.objects.get_or_create(
                            user=user,
                            meal_type='lunch',
                            recorded_at__date=date
                        )
                        # ここでは簡略化のため、食品名とカロリーだけをダミーで登録
                        MealItem.objects.create(
                            meal=meal,
                            food_name=f"ダミー食品(ID:{row['meal_barcode']})",
                            calories=float(row['meal_calories']),
                            quantity=100,
                            unit='g'
                        )

            self.stdout.write(self.style.SUCCESS(f'{username} のダミーデータの登録が完了しました。'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'{csv_path} が見つかりません。'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'エラーが発生しました: {e}'))