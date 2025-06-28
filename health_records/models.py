from django.db import models

# Create your models here.
# health_records/models.py

from django.db import models
from django.conf import settings # settings.AUTH_USER_MODEL を使うため

# タグモデルを定義
class Tag(models.Model):
    """
    健康記録に付けるタグのモデル
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='タグ名')

    def __str__(self):
        return self.name
    

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

   
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='タグ')
    notes = models.TextField(blank=True, null=True, verbose_name='メモ')

    def __str__(self):
        # 管理画面などで表示されるときの文字列
        return f"{self.user.username} - {self.get_record_type_display()} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-recorded_at'] # 新しい記録から順に表示する
        verbose_name = '健康記録'
        verbose_name_plural = '健康記録'


# health_records/models.py

# ... (既存のHealthRecord, Tagモデルはそのまま) ...

# --- ★ここから新しいSleepRecordモデルを追加 ---
from django.core.validators import MinValueValidator, MaxValueValidator

class SleepRecord(models.Model):
    """
    睡眠に特化した記録を保存するモデル
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sleep_records', verbose_name='ユーザー')
    start_time = models.DateTimeField(verbose_name='就寝時刻')
    end_time = models.DateTimeField(verbose_name='起床時刻')

    # blank=Trueにすることで、管理画面などでは空欄を許可（自動計算するため）
    duration = models.DurationField(verbose_name='睡眠時間', blank=True)

    quality_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True, 
        verbose_name='睡眠の質 (1-5)'
    )
    notes = models.TextField(blank=True, verbose_name='メモ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        ordering = ['-start_time']

    def save(self, *args, **kwargs):
        # 就寝時刻と起床時刻から、睡眠時間を自動計算して保存
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s sleep on {self.start_time.date()}"

# health_records/models.py

# ... 既存の HealthRecord モデルの下に ...

# --- ★ここから新しいモデルを追加 ---
from django.core.validators import MinValueValidator, MaxValueValidator

class SleepChronotypeSurvey(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sleep_survey',
        verbose_name='ユーザー'
    )
    # 平日の睡眠
    weekday_bedtime = models.TimeField(verbose_name='平日の就寝時刻', null=True, blank=True)
    weekday_wakeup_time = models.TimeField(verbose_name='平日の起床時刻', null=True, blank=True)
    
    # 休日の睡眠
    weekend_bedtime = models.TimeField(verbose_name='休日の就寝時刻', null=True, blank=True)
    uses_alarm_on_weekend = models.BooleanField(default=True, verbose_name='休日にアラームを使うか')
    weekend_natural_wakeup_time = models.TimeField(
        verbose_name='休日に自然に起きる時刻',
        help_text='もしアラームをかけなかった場合に起きるであろう時刻',
        null=True, blank=True
    )

    # 睡眠の質
    sleep_quality = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='朝の目覚めの良さ (1-5)',
        null=True, blank=True
    )
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    def __str__(self):
        return f"{self.user.username} の睡眠アンケート"

    class Meta:
        verbose_name = '睡眠クロノタイプアンケート'
        verbose_name_plural = '睡眠クロノタイプアンケート'