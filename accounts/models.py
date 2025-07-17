from django.db import models
from django.conf import settings # settings.AUTH_USER_MODEL を使うため
# from django.contrib.auth.models import User # もし標準Userモデルを直接参照する場合


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='生年月日')
    
    GENDER_CHOICES = [
        ('male', '男性'),
        ('female', '女性'),
        ('other', 'その他'),
        ('prefer_not_to_say', '回答しない'),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True, verbose_name='性別')
    profile_picture_url = models.URLField(max_length=255, null=True, blank=True, verbose_name='プロフィール画像URL')
    
    # --- 身体情報 ---
    height_cm = models.FloatField(null=True, blank=True, verbose_name='身長 (cm)')
    
    ACTIVITY_LEVEL_CHOICES = [
        (1.2,   '低い (ほとんど運動しない)'),
        (1.375, '普通 (週に1-3回程度の運動)'),
        (1.55,  '高い (週に3-5回程度の運動)'),
        (1.725, '非常に高い (週に6-7回運動する)'),
        (1.9,   '超高い (非常に激しい運動)'),
    ]
    activity_level = models.FloatField(
        choices=ACTIVITY_LEVEL_CHOICES,
        default=1.375, # デフォルト値を「普通」に設定
        verbose_name='身体活動レベル'
    )
    
    # --- 目標設定 ---
    target_weight = models.FloatField(null=True, blank=True, verbose_name='目標体重 (kg)')
    target_steps_per_day = models.PositiveIntegerField(null=True, blank=True, verbose_name='目標歩数/日')
    target_calories = models.PositiveIntegerField(null=True, blank=True, verbose_name='目標カロリー (kcal)')
    target_protein = models.FloatField(null=True, blank=True, verbose_name='目標タンパク質 (g)')
    target_fat = models.FloatField(null=True, blank=True, verbose_name='目標脂質 (g)')
    target_carbohydrate = models.FloatField(null=True, blank=True, verbose_name='目標炭水化物 (g)')
    
    # --- Big Five用のフィールド ---
    big5_openness = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='ビッグファイブ：開放性')
    big5_conscientiousness = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='ビッグファイブ：誠実性')
    big5_extraversion = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='ビッグファイブ：外向性')
    big5_agreeableness = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='ビッグファイブ：協調性')
    big5_neuroticism = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='ビッグファイブ：神経症的傾向')
    
    # --- アプリの状態管理 ---
    onboarding_complete = models.BooleanField(default=False, verbose_name='初期設定完了フラグ')

    def __str__(self):
        return f"{self.user.username}'s Profile"
    

    
    # --- ★ここから新しい設定項目を追加 ---
    NUTRITION_PRIORITY_CHOICES = [
        ('balance', '全体的なバランスを重視'),
        ('protein_first', 'タンパク質を最優先'),
        ('low_calorie', 'カロリーを抑えることを最優先'),
        ('energy_up', '炭水化物を優先してエネルギー補給'),
    ]
    nutrition_priority = models.CharField(
        max_length=20,
        choices=NUTRITION_PRIORITY_CHOICES,
        default='balance',
        verbose_name='栄養摂取の優先順位'
    )
    # --- ★ここまで追加 ---
    
    # ...

# ↓ --- ここからシグナルのコードを追加 --- ↓

from django.db.models.signals import post_save
from django.dispatch import receiver

# @receiverデコレータで、どのシグナルを監視するかを指定
# 今回は、Userモデル(settings.AUTH_USER_MODEL)が保存された後(post_save)のシグナルを監視
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    新しいユーザーが作成されたときに、自動的にUserProfileを作成する。
    """
    # 'created' は、この保存が「新規作成」の場合に True になるフラグ
    if created:
        UserProfile.objects.create(user=instance)

# (参考) 既存のユーザー情報が更新されたときに、プロフィールも一緒に保存するためのシグナル
# こちらは必須ではありませんが、一般的にセットで実装されることが多いです
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
# accounts/models.py の一番下に追加






# --- ★ここから新しい UserDevice モデルを追加 ---
class UserDevice(models.Model):
    """
    ユーザーのデバイス情報を保存するモデル
    """
    # どのユーザーのデバイスか
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices')

    # デバイストークン (非常に長くなる可能性があるためTextField)
    # 同じトークンが複数登録されないように unique=True
    device_token = models.TextField(unique=True, verbose_name='デバイストークン')

    # プラットフォーム (iOSかAndroidか)
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
    ]
    platform = models.CharField(
        max_length=10, 
        choices=PLATFORM_CHOICES, 
        verbose_name='プラットフォーム'
    )

    is_active = models.BooleanField(default=True, verbose_name='有効フラグ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        verbose_name = 'ユーザーデバイス'
        verbose_name_plural = 'ユーザーデバイス'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.get_platform_display()} Device"