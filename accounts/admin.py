from django.contrib import admin
from .models import UserProfile # 作成した UserProfile モデルをインポート

# UserProfile モデルを管理画面に登録
admin.site.register(UserProfile)