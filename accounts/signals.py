from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User  # Django標準のUserモデル
from .models import UserProfile             # あなたが作成したプロフィールモデル

#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
    #if created:
        # 既に存在しないことを確認してから作成
        #if not hasattr(instance, 'userprofile'):
           # UserProfile.objects.create(user=instance)

# もしUserモデルの更新時にも何かしたい場合は、ここに追加できる
# post_save.connect(create_user_profile, sender=User) # この行は@receiverデコレータを使っているなら不要