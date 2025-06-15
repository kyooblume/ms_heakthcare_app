from django.shortcuts import render

# Create your views here.
# health_records/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated # 認証されたユーザーのみアクセス許可
from rest_framework.response import Response
from .models import HealthRecord
from .serializers import HealthRecordSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated # AllowAny を追加 (IsAuthenticated も念のため一緒に)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Sum, Max, Min # 集計機能を使うためにインポート


class HealthRecordViewSet(viewsets.ModelViewSet):
    """
    健康記録のCRUD操作を行うためのAPIビューセット。
    - 認証されたユーザーのみアクセス可能。
    - ユーザーは自身の健康記録のみを閲覧・編集・削除できる。
    """
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated] # このビューセットへのアクセスには認証（ログイン）が必須
    #permission_classes = [AllowAny]
        # ↓ どのフィールドでフィルタリングを許可するか指定
    filterset_fields = ['record_type'] # record_type フィールドでフィルタリングを許可

    def get_queryset(self):
        """
        このビューセットが返すクエリセット（データの集合）をカスタマイズします。
        現在のリクエストユーザーに紐づく健康記録のみを返すようにします。
        これにより、他のユーザーの記録は見えなくなります。
        """
        user = self.request.user
        # is_authenticated は IsAuthenticated パーミッションクラスによって既に保証されていますが、
        # 明示的に確認しておくとより安全です。
        if user.is_authenticated:
            return HealthRecord.objects.filter(user=user).order_by('-recorded_at')
        # 認証されていない場合は空のクエリセットを返します (通常、permission_classesでブロックされるため到達しません)
        return HealthRecord.objects.none()

    def perform_create(self, serializer):
        """
        新しい健康記録が作成される際に追加の処理を行うためのメソッドです。
        記録の 'user' フィールドに、現在リクエストを行っている認証済みユーザーを自動的にセットします。
        これにより、クライアントはuserフィールドをリクエストに含める必要がなくなります。
        """
        serializer.save(user=self.request.user)



    def create(self, request, *args, **kwargs):
        # 送られてきたデータをシリアライザーで検証
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 検証済みデータから必要な情報を取り出す
        record_type = serializer.validated_data.get('record_type')
        # 日付単位で重複をチェックするため、今日の日付を取得
        # (より高度にするなら、リクエストから日付を受け取ることも可能)
        today = timezone.now().date()

        # "もし今日、同じ種類の記録が既にあれば更新、なければ新規作成" を行う
        record, created = HealthRecord.objects.update_or_create(
            user=request.user,
            record_type=record_type,
            recorded_at__date=today, # recorded_atの日付部分が今日のもの、という条件
            # 存在しなかった場合に、新しいレコードに設定される値
            defaults=serializer.validated_data
        )

        # 作成または更新されたレコードのデータを、改めてシリアライザーで整形
        response_serializer = self.get_serializer(record)

        # 新規作成なら 201 Created、更新なら 200 OK を返す
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK

        return Response(response_serializer.data, status=status_code)



# --- ★「今週の健康サマリー」用の新しいビュークラス ---
class HealthSummaryView(APIView):
    """
    過去7日間の健康記録のサマリーを返す、読み取り専用のAPIビュー。
    """
    permission_classes = [IsAuthenticated] # 認証されたユーザーのみアクセス可能

    def get(self, request, *args, **kwargs):
        # GETリクエストが来たときにこのメソッドが実行される

        # 1. ユーザーと期間を定義
        user = request.user
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)

        # 2. 期間内のユーザーの健康記録を取得
        records_in_period = HealthRecord.objects.filter(
            user=user,
            recorded_at__range=(start_date, end_date)
        )

        # 3. 各項目のサマリーを計算
        # 歩数 (合計と平均)
        steps_records = records_in_period.filter(record_type='steps')
        steps_summary = steps_records.aggregate(
            total_steps=Sum('value_numeric'),
            average_steps=Avg('value_numeric')
        )

        # 睡眠時間 (平均)
        sleep_summary = records_in_period.filter(record_type='sleep').aggregate(
            average_sleep=Avg('value_numeric')
        )

        # 心拍数 (最小, 最大, 平均)
        heart_rate_summary = records_in_period.filter(record_type='heart_rate').aggregate(
            min_hr=Min('value_numeric'),
            max_hr=Max('value_numeric'),
            avg_hr=Avg('value_numeric')
        )

        # 最新の体重
        latest_weight_record = records_in_period.filter(record_type='weight').order_by('-recorded_at').first()
        latest_weight = latest_weight_record.value_numeric if latest_weight_record else None


        # 4. レスポンスとして返すデータを作成
        summary_data = {
            'user': user.username,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_steps': steps_summary.get('total_steps') or 0,
            'average_steps': steps_summary.get('average_steps') or 0,
            'average_sleep_hours': sleep_summary.get('average_sleep') or 0,
            'latest_weight_kg': latest_weight,
            'heart_rate_summary': {
                'min': heart_rate_summary.get('min_hr'),
                'max': heart_rate_summary.get('max_hr'),
                'average': heart_rate_summary.get('avg_hr')
            }
        }

        # 5. データをJSON形式で返す
        return Response(summary_data, status=status.HTTP_200_OK)
# --- ★ここまで「今週の健康サマリー」用の新しいビュークラス ---
# このビューは、ユーザーの健康記録を集計して、過去7日間のサマリーを提供します。