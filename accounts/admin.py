from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserDevice, HealthData

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
    #inlines = (UserProfileInline,)
    def get_inlines(self, request, obj=None):
        # obj is the user object being edited.
        # It will be None when creating a new user.
        if obj: # ★★★ 既存ユーザーの編集時 (objが存在する時) のみインラインを表示 ★★★
            return (UserProfileInline,)
        else:
            return ()
# --- メインの登録処理 ---
# DjangoのデフォルトUserAdminを解除
#admin.site.unregister(User)
# プロフィール付きの新しいUserAdminを登録
#admin.site.register(User, UserAdmin)
# UserDeviceモデルは単独で登録
admin.site.register(UserDevice)
# UserProfileモデルを管理画面に登録
admin.site.register(UserProfile)

# HealthDataモデルを管理画面に登録
@admin.register(HealthData)
class HealthDataAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'date', 'steps', 'sleep_minutes')
    list_filter = ('date',)
    search_fields = ('user_profile__user__username',)