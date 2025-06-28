# reports/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datetime import datetime

# データベースの機能と、他のアプリのモデルをインポート
from django.db.models import Count, Avg, Max, Min, F, Window
from django.db.models.functions import Rank
from health_records.models import HealthRecord

from health_records.models import HealthRecord, SleepChronotypeSurvey
from datetime import datetime, time, timedelta

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