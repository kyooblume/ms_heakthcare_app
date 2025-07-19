# reports/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datetime import datetime

# データベースの機能と、他のアプリのモデルをインポート
from django.db.models import Count, Avg, Max, Min, F, Window
from django.db.models.functions import Rank
from health_records.models import HealthRecord, SleepChronotypeSurvey
from datetime import datetime, time, timedelta
from django.utils import timezone
from accounts.models import UserProfile
from datetime import timedelta
from django.db.models import Avg # 平均を計算するためにインポート




from datetime import datetime, timedelta
from django.db.models import Sum, F, Window, Avg
from django.db.models.functions import Rank, Abs



class StepRankingReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "無効な日付形式です。YYYY-MM-DDで指定してください。"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # 1. その日の歩数記録を持つ全ユーザーのデータを、順位付けしながら取得
        all_steps_today = HealthRecord.objects.filter(
            record_type='steps',
            recorded_at__date=target_date
        ).annotate(
            # F()は自分のフィールドの値を参照し、Window()とRank()で順位を計算
            rank=Window(
                expression=Rank(),
                order_by=F('value_numeric').desc() # 歩数が多い順
            )
        )

        # 2. 自分の順位付けされた記録を取得
        my_ranked_record = all_steps_today.filter(user=user).first()
        if not my_ranked_record:
            return Response({"error": f"{date_str} の歩数記録が見つかりません。"}, status=status.HTTP_404_NOT_FOUND)

        # 3. 全体の統計情報を一括で計算
        stats = all_steps_today.aggregate(
            total_participants=Count('id'),
            average=Avg('value_numeric'),
            max=Max('value_numeric'),
            min=Min('value_numeric')
        )
        if stats['total_participants'] == 0:
            return Response({"error": "今日の歩数記録がまだ誰もありません。"})

        # 4. 上位何パーセントにいるかを計算
        percentile = (stats['total_participants'] - my_ranked_record.rank) / (stats['total_participants'] - 1) * 100 if stats['total_participants'] > 1 else 100

        # 5. レスポンスデータを作成
        response_data = {
            "date": target_date,
            "my_steps": my_ranked_record.value_numeric,
            "my_rank": my_ranked_record.rank,
            "total_participants": stats['total_participants'],
            "top_percentile": 100 - round(percentile), # あなたは上位〇%です、という表現
            "statistics": {
                "average": round(stats['average'] or 0),
                "max": stats['max'] or 0,
                "min": stats['min'] or 0,
            }
        }
        return Response(response_data)
    


class SocialJetlagReportView(APIView):
    """
    社会的ジェットラグの少なさ（体内時計の正確さ）に基づいたランキングを返す。
    このレポートは特定の日付に依存しないため、日付のパラメータは不要。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        all_surveys = SleepChronotypeSurvey.objects.select_related('user').all()

        if not all_surveys.exists():
            return Response({"error": "まだ誰も睡眠アンケートに回答していません。"}, status=status.HTTP_404_NOT_FOUND)

        # 全ユーザーの社会的ジェットラグを計算
        user_jetlags = []
        for survey in all_surveys:
            # 1. 平日の睡眠中央時刻を計算
            weekday_midpoint = self._calculate_midpoint(survey.weekday_bedtime, survey.weekday_wakeup_time)
            
            # 2. 休日の睡眠中央時刻を計算
            weekend_midpoint = self._calculate_midpoint(survey.weekend_bedtime, survey.weekend_natural_wakeup_time)

            # 3. 社会的ジェットラグを分単位で計算
            jetlag_minutes = abs(weekday_midpoint - weekend_midpoint).total_seconds() / 60
            
            user_jetlags.append({
                "username": survey.user.username,
                "jetlag_minutes": jetlag_minutes
            })

        # 4. ジェットラグが少ない順に並び替え
        sorted_users = sorted(user_jetlags, key=lambda x: x['jetlag_minutes'])

        # 5. 順位を付けて、自分の情報を探す
        my_rank_data = None
        for i, data in enumerate(sorted_users):
            data['rank'] = i + 1
            if data['username'] == user.username:
                my_rank_data = data
        
        if not my_rank_data:
             return Response({"error": "あなたがまだ睡眠アンケートに回答していません。"}, status=status.HTTP_404_NOT_FOUND)

        # 6. レスポンスデータを作成
        total_participants = len(sorted_users)
        percentile = (total_participants - my_rank_data['rank']) / (total_participants - 1) * 100 if total_participants > 1 else 100

        response_data = {
            "my_social_jetlag_hours": round(my_rank_data['jetlag_minutes'] / 60, 2), # 時間に変換
            "my_rank": my_rank_data['rank'],
            "total_participants": total_participants,
            "top_percentile": 100 - round(percentile)
        }
        return Response(response_data)

    def _calculate_midpoint(self, bedtime, wakeup_time):
        """睡眠の中央時刻を計算するヘルパーメソッド"""
        # 日付をまたぐ睡眠を考慮
        bed_datetime = datetime.combine(datetime.today(), bedtime)
        wake_datetime = datetime.combine(datetime.today(), wakeup_time)
        if wake_datetime < bed_datetime:
            wake_datetime += timedelta(days=1)
            
        duration = wake_datetime - bed_datetime
        midpoint = bed_datetime + duration / 2
        return midpoint
    


#
class DailyActivityReportView(APIView):
    """
    指定された日の活動量（歩数）の目標、実績、達成率を返すビュー。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "無効な日付形式です。YYYY-MM-DDで指定してください。"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # 1. 目標歩数を取得
        target_steps = 0
        try:
            profile = user.userprofile
            target_steps = profile.target_steps_per_day or 0
        except UserProfile.DoesNotExist:
            pass

        # 2. 実績歩数を取得
        actual_steps = 0
        try:
            record = HealthRecord.objects.get(user=user, record_type='steps', recorded_at__date=target_date)
            actual_steps = record.value_numeric or 0
        except HealthRecord.DoesNotExist:
            pass
            
        # 3. 達成率を計算
        achievement_rate = 0
        if target_steps > 0:
            achievement_rate = round((actual_steps / target_steps) * 100)

        # 4. レスポンスデータを作成
        response_data = {
            "date": target_date,
            "steps": {
                "target": target_steps,
                "actual": int(actual_steps),
                "achievement_rate": achievement_rate 
            }
        }
        return Response(response_data)
    

class WeeklySleepReportView(APIView):
    """
    過去7日間の睡眠記録を返すビュー。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        week_ago = today - timedelta(days=6)
        
        # 過去7日間の睡眠記録を取得
        sleep_records = HealthRecord.objects.filter(
            user=user, 
            record_type='sleep',
            recorded_at__date__range=[week_ago, today]
        ).order_by('recorded_at')
        
        # 日付ごとの睡眠時間を整理
        # { '2025-07-10': 7.5, '2025-07-11': 6.0, ... } のような形式にする
        report_data = {}
        for i in range(7):
            date = week_ago + timedelta(days=i)
            report_data[date.strftime('%Y-%m-%d')] = 0 # まず0で初期化
        
        for record in sleep_records:
            date_str = record.recorded_at.strftime('%Y-%m-%d')
            report_data[date_str] = record.value_numeric # 実績値で上書き
            
        return Response(report_data)
    


class DailyActivityReportView(APIView):
    """
    指定された日の活動量（歩数）の目標、実績、達成率を返す、より安全なビュー。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "無効な日付形式です。YYYY-MM-DDで指定してください。"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # 1. 目標歩数を安全に取得
        target_steps = 0
        try:
            # user.userprofile の代わりに、UserProfile.objects.get() を使って安全に取得
            profile = UserProfile.objects.get(user=user)
            target_steps = profile.target_steps_per_day or 0
        except UserProfile.DoesNotExist:
            # プロフィールが存在しない場合は、目標を0として扱う
            pass

        # 2. 実績歩数を安全に取得
        actual_steps = 0
        try:
            # .get() はデータがないとエラーになるので、.filter().first() を使うのがより安全
            record = HealthRecord.objects.filter(user=user, record_type='steps', recorded_at__date=target_date).first()
            if record:
                actual_steps = record.value_numeric or 0
        except HealthRecord.DoesNotExist:
            # 記録がなくてもエラーにしない
            pass
            
        # 3. 達成率を計算
        achievement_rate = round((actual_steps / target_steps) * 100) if target_steps > 0 else 0

        response_data = {
            "date": target_date,
            "steps": {
                "target": int(target_steps),
                "actual": int(actual_steps),
                "achievement_rate": achievement_rate 
            }
        }
        return Response(response_data)


class WeeklySleepReportView(APIView):
    """
    過去7日間の睡眠記録を返すビュー。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        week_ago = today - timedelta(days=6)
        
        sleep_records = HealthRecord.objects.filter(
            user=user, 
            record_type='sleep',
            recorded_at__date__range=[week_ago, today]
        ).order_by('recorded_at')
        
        report_data = {}
        for i in range(7):
            date = week_ago + timedelta(days=i)
            report_data[date.strftime('%Y-%m-%d')] = 0
        
        for record in sleep_records:
            date_str = record.recorded_at.strftime('%Y-%m-%d')
            report_data[date_str] = record.value_numeric
            
        return Response(report_data)




# --- ★DashboardSummaryView を、この新しいコードに丸ごと置き換えてください ---
class DashboardSummaryView(APIView):
    """
    ダッシュボードに必要な全てのサマリーデータを一度に返す、万能APIビュー。(完成版)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # --- 1. 歩数データの計算 ---
        target_steps = 0
        try:
            # プロフィールが存在しなくてもエラーにならないように、get_or_create を使用
            profile, created = UserProfile.objects.get_or_create(user=user)
            target_steps = profile.target_steps_per_day or 0
        except UserProfile.DoesNotExist:
            pass

        # 今日の歩数
        today_steps_record = HealthRecord.objects.filter(user=user, record_type='steps', recorded_at__date=today).first()
        today_steps = today_steps_record.value_numeric if today_steps_record else 0
        
        # --- ★ここが修正ポイントです！ ---
        # 週間平均歩数 (今日を含めた、過去7日間)
        week_ago = today - timedelta(days=6) # 7ではなく6が正しい
        weekly_avg_data = HealthRecord.objects.filter(
            user=user, record_type='steps', recorded_at__date__gte=week_ago, recorded_at__date__lte=today
        ).aggregate(average=Avg('value_numeric'))
        weekly_avg_steps = weekly_avg_data.get('average') or 0

        # 月間平均歩数 (今日を含めた、過去30日間)
        month_ago = today - timedelta(days=29) # 30ではなく29が正しい
        monthly_avg_data = HealthRecord.objects.filter(
            user=user, record_type='steps', recorded_at__date__gte=month_ago, recorded_at__date__lte=today
        ).aggregate(average=Avg('value_numeric'))
        monthly_avg_steps = monthly_avg_data.get('average') or 0
        # --- ★ここまでが修正ポイント ---

        # --- 2. 睡眠データの計算 (週間) ---
        # (ここは変更なし)
        sleep_records = HealthRecord.objects.filter(
            user=user, record_type='sleep', recorded_at__date__range=[week_ago, today]
        ).order_by('recorded_at')
        
        weekly_sleep_data = {}
        for i in range(7):
            date = week_ago + timedelta(days=i)
            weekly_sleep_data[date.strftime('%Y-%m-%d')] = 0
        for record in sleep_records:
            date_str = record.recorded_at.strftime('%Y-%m-%d')
            weekly_sleep_data[date_str] = record.value_numeric

        # --- 3. レスポンスデータをまとめる ---
        response_data = {
            "activity": {
                "today_steps": int(today_steps),
                "target_steps": int(target_steps),
                "weekly_average_steps": int(weekly_avg_steps),
                "monthly_average_steps": int(monthly_avg_steps)
            },
            "sleep": {
                "weekly_summary": weekly_sleep_data
            }
        }
        return Response(response_data)

