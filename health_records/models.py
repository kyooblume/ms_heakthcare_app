from django.db import models

# Create your models here.
# health_records/models.py

from django.db import models
from django.conf import settings # settings.AUTH_USER_MODEL を使うため

class HealthRecord(models.Model):
    # 記録の種類を定義 (選択肢として利用)
    RECORD_TYPE_CHOICES = [
        ('weight', '体重 (kg)'),
        ('steps', '歩数'),
        ('sleep', '睡眠時間 (時間)'),
        ('temperature', '体温 (℃)'),
        ('blood_pressure', '血圧 (mmHg)'),
        ('mood', '気分'),
        ('meal', '食事メモ'),
        ('exercise', '運動メモ'),
        ('hydration', '水分摂取量 (ml)'),
        ('blood_oxygen', '血中酸素濃度 (%)'),  # 血中酸素濃度の記録
        ('heart_rate', '心拍数 (bpm)'),  # 心拍数の記録
        ('body_fat', '体脂肪率 (%)'),  # 体脂肪率の記録
        ('muscle_mass', '筋肉量 (kg)'),  # 筋肉量の記録     
        ('waist_circumference', 'ウエスト周囲長 (cm)'),  # ウエスト周囲長の記録
        ('physical_activity', '身体活動レベル'),  # 身体活動レベルの記録
        ('stress_level', 'ストレスレベル'),  # ストレスレベルの記録
        ('nutrition', '栄養摂取記録'),  # 栄養摂取の記録
        ('sleep_quality', '睡眠の質'),  # 睡眠の質の記録
        ('health_goals', '健康目標設定'),  # 健康目標の設定
        ('supplements', 'サプリメント摂取記録'),  # サプリメントの摂取記録
        ('exercise_intensity', '運動強度'),  # 運動の強度の記録

        
        # 必要に応じて他の記録タイプを追加
    ]

    # どのユーザーの記録か (Userモデルと連携)
    # settings.AUTH_USER_MODEL を使うことで、カスタムユーザーモデルにも対応しやすくなります。
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='health_records')

    # 記録の種類
    record_type = models.CharField(
        max_length=50,
        choices=RECORD_TYPE_CHOICES,
        verbose_name='記録の種類'
    )

    # 記録された値 (数値データの場合)
    value_numeric = models.FloatField(null=True, blank=True, verbose_name='数値')
    # 記録された値 (テキストデータの場合、例: 気分、食事メモ)
    value_text = models.TextField(null=True, blank=True, verbose_name='テキスト値')

    # 記録日時 (入力時に自動で現在日時が設定される)
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name='記録日時')
    # ユーザーが任意の日時で記録したい場合は auto_now_add=False にして、
    # default=timezone.now や、入力フィールドにする必要があります。
    # 今回はシンプルに自動記録とします。

    # メモ (任意)
    notes = models.TextField(blank=True, null=True, verbose_name='メモ')

    def __str__(self):
        # 管理画面などで表示されるときの文字列
        return f"{self.user.username} - {self.get_record_type_display()} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-recorded_at'] # 新しい記録から順に表示する
        verbose_name = '健康記録'
        verbose_name_plural = '健康記録'