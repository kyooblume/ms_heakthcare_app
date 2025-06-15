# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserDevice

# UserProfileをUserの管理画面内で一緒に編集できるようにするための設定
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'プロフィール'

# 既存のUserの管理画面を拡張するための設定
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# --- メインの処理 ---
# 1. Djangoがデフォルトで登録しているUserの管理画面を一旦解除
admin.site.unregister(User)
# 2. 上で定義した、プロフィールも一緒に編集できる新しいUser管理画面を登録
admin.site.register(User, UserAdmin)

# UserDeviceモデルはこれまで通り、単独で登録
admin.site.register(UserDevice)