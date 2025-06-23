from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserDevice

# UserProfileをUserの管理画面内で一緒に編集できるようにするための設定 (Inline)
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'プロフィール'
    
    # ↓ ★★★ fields の設定は、こちらのクラスに書きます ★★★
    fields = ('date_of_birth', 'gender', 'height_cm', 'activity_level','target_weight', 'target_steps_per_day', 
              'target_calories', 'target_protein', 'target_fat', 'target_carbohydrate')

# 既存のUserの管理画面を拡張するための設定
class UserAdmin(BaseUserAdmin):
    # こちらには、UserProfileInline を連結する設定だけを書きます
    inlines = (UserProfileInline,)

# --- メインの登録処理 ---
# DjangoのデフォルトUserAdminを解除
admin.site.unregister(User)
# プロフィール付きの新しいUserAdminを登録
admin.site.register(User, UserAdmin)

# UserDeviceモデルは単独で登録
admin.site.register(UserDevice)