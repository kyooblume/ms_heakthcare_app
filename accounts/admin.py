# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile
from health_records.models import HealthRecord
from meals.models import Meal


# --- 1. ユーザーページに「追加」したい情報を、種類ごとに専用のインラインとして定義 ---

# UserProfile用のインライン (これは変更なし)
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'プロフィール'

# --- ★ここからが新しい部分です！ ---

# 「歩数」専用のインライン
class StepsRecordInline(admin.TabularInline):
    model = HealthRecord
    verbose_name_plural = '歩数記録' # 管理画面での表示名
    extra = 0
    fields = ('value_numeric', 'recorded_at')
    #readonly_fields = ('recorded_at',)

    # このインラインが表示するデータを、「歩数」だけに絞り込む
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(record_type='steps')

# 「睡眠時間」専用のインライン
class SleepRecordInline(admin.TabularInline):
    model = HealthRecord
    verbose_name_plural = '睡眠記録 (時間)'
    extra = 0
    fields = ('value_numeric', 'recorded_at')
    #readonly_fields = ('recorded_at',)

    # このインラインが表示するデータを、「睡眠時間」だけに絞り込む
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(record_type='sleep')

# 「体重」専用のインライン
class WeightRecordInline(admin.TabularInline):
    model = HealthRecord
    verbose_name_plural = '体重記録'
    extra = 0
    fields = ('value_numeric', 'recorded_at')
    #readonly_fields = ('recorded_at',)

    # このインラインが表示するデータを、「体重」だけに絞り込む
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(record_type='weight')

# --- ★ここまでが新しい部分です！ ---

# 食事記録用のインライン (これは変更なし)
class MealInline(admin.TabularInline):
    model = Meal
    extra = 0
    fields = ('meal_type', 'recorded_at')
    #readonly_fields = ('recorded_at',)
    verbose_name_plural = '食事記録'


# --- 2. 新しいUserAdminクラスを定義し、新しい専用インラインを使うように変更 ---

class CustomUserAdmin(BaseUserAdmin):
    # Userページに、上で定義したインラインを登録
    # 以前のHealthRecordInlineの代わりに、種類別の専用インラインを追加
    inlines = (
        UserProfileInline, 
        StepsRecordInline, 
        SleepRecordInline, 
        WeightRecordInline, 
        MealInline
    )

# --- 3. 最後に、Djangoに新しいUserAdminを登録 (ここは変更なし) ---
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)