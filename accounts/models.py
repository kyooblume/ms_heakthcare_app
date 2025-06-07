from django.db import models
from django.conf import settings # settings.AUTH_USER_MODEL を使うため
# from django.contrib.auth.models import User # もし標準Userモデルを直接参照する場合

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='生年月日')
    GENDER_CHOICES = [
        ('male', '男性'),
        ('female', '女性'),
        ('other', 'その他'),
        ('prefer_not_to_say', '回答しない'),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True, verbose_name='性別')
    profile_picture_url = models.URLField(max_length=255, null=True, blank=True, verbose_name='プロフィール画像URL')
    # その他、目標設定などアプリ特有のユーザー情報を追加
    target_weight = models.FloatField(null=True, blank=True, verbose_name='目標体重 (kg)')
    target_steps_per_day = models.PositiveIntegerField(null=True, blank=True, verbose_name='目標歩数/日')

    def __str__(self):
        return f"{self.user.username}'s Profile"
    



class UserProfile(models.Model):
    # Userモデルと1対1の関係で紐付けます
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,    # どのユーザーモデルと連携するか
        on_delete=models.CASCADE,  # 連携するユーザーが削除されたら、このプロフィールも一緒に削除
        related_name='profile',      # user.profile のように逆参照（アクセス）できるようになる
        verbose_name='ユーザー'
    )

    # ここから、追加したいプロフィール情報をフィールドとして定義していきます
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='生年月日')

    GENDER_CHOICES = [
        ('male', '男性'),
        ('female', '女性'),
        ('other', 'その他'),
        ('prefer_not_to_say', '回答しない'),
    ]
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        null=True, 
        blank=True, # null=True, blank=True は、この項目が任意（入力しなくてもOK）であることを示す
        verbose_name='性別'
    )

    target_weight = models.FloatField(null=True, blank=True, verbose_name='目標体重 (kg)')
    target_steps_per_day = models.PositiveIntegerField(null=True, blank=True, verbose_name='目標歩数/日')

    def __str__(self):
        # 管理画面などで表示されるときの名前
        return f"{self.user.username}'s Profile"

    class Meta:
        # 管理画面で表示されるモデル名
        verbose_name = 'ユーザープロフィール'
        verbose_name_plural = 'ユーザープロフィール'


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

from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.conf import settings は、ファイルの先頭あたりに既にあるはずです

# Userモデルの post_save シグナルを監視する
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    新しいユーザーが作成されたときに、自動的にUserProfileを作成する。
    """
    if created: # 新規作成の場合のみ
        UserProfile.objects.create(user=instance)




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