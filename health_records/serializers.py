# health_records/serializers.py

from rest_framework import serializers
from .models import HealthRecord, Tag, SleepRecord
from .models import HealthRecord, SleepChronotypeSurvey, SleepSession

# from django.contrib.auth.models import User # Userモデルを直接参照する場合に備えてコメントアウト

# --- ★ここから新しい TagSerializer を追加 ---
class TagSerializer(serializers.ModelSerializer):
    """
    Tagモデル用のシリアライザー
    """
    class Meta:
        model = Tag
        fields = ['id', 'name']

class HealthRecordSerializer(serializers.ModelSerializer):
    # user フィールドは、APIレスポンスでユーザー名を表示するようにカスタマイズする例
    # source='user.username' は、HealthRecordモデルのuserフィールドの先のusername属性を参照します。
    # read_only=True なので、このシリアライザー経由でuserフィールドを書き換えることはできません。
    # (ユーザーの割り当てはビュー側で行います)
    user_username = serializers.CharField(source='user.username', read_only=True)

        # ↓ ★ここからタグ用の設定を追加・変更します
    tags = serializers.SlugRelatedField(
        many=True,                       # 複数のタグを扱えるようにする
        slug_field='name',                 # タグをIDではなく、'name'フィールド（タグ名）で表現する
        queryset=Tag.objects.all(),        # 有効なタグのリスト（書き込み時の検証に使う）
        required=False                     # タグの指定は任意項目にする
    )
    # ↑ ★ここまで



    class Meta:
        model = HealthRecord  # どのモデルをベースにするか指定
        # APIでやり取りするフィールドを指定
        fields = [
            'id',
            'user',             # 記録作成時はビューで設定。読み取り時はユーザーID。
            'user_username',    # 読み取り時にユーザー名を表示するための追加フィールド
            'record_type',
            'get_record_type_display', # モデルのメソッドを使って表示名を取得
            'value_numeric',
            'value_text',
            'recorded_at',
            'notes',
            'tags',  # タグを追加
        ]
        # 以下のフィールドは、API経由でクライアントから直接指定させず、
        # ビューで自動的に設定したり、モデルで自動設定されたりするものです。
        read_only_fields = ('user', 'recorded_at', 'user_username', 'get_record_type_display')

        # もし特定のフィールドのバリデーションを追加したい場合は、
        # validate_<field_name> メソッドや validate メソッドをここに書けます。
        # 例:
        # def validate_value_numeric(self, value):
        #     if self.instance and self.instance.record_type == 'steps' and value < 0:
        #         raise serializers.ValidationError("歩数は0以上である必要があります。")
        #     return value

# 参考: もしユーザー情報をネストして表示したい場合 (より高度)
# class UserForHealthRecordSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User # from django.contrib.auth.models import User が必要
#         fields = ['id', 'username', 'email']

# class HealthRecordSerializerWithNestedUser(serializers.ModelSerializer):
#     user = UserForHealthRecordSerializer(read_only=True) # ネストされたユーザー情報
#     class Meta:
#         model = HealthRecord
#         fields = ['id', 'user', 'record_type', 'value_numeric', 'value_text', 'recorded_at', 'notes']
#         read_only_fields = ('recorded_at',)





# ... (既存の HealthRecordSerializer, TagSerializer はそのまま) ...

# --- ★ここから新しい SleepRecordSerializer を追加 ---
class SleepRecordSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    # 睡眠時間(duration)はモデルのsave()で自動計算されるので、読み取り専用にします
    duration = serializers.DurationField(read_only=True)

    class Meta:
        model = SleepRecord
        # APIでやり取りするフィールドを指定します
        fields = [
            'id', 'user_username', 'start_time', 'end_time', 
            'duration', 'quality_rating', 'notes', 'created_at'
        ]
        # user, duration, created_atなどは、バックエンド側で自動設定するので読み取り専用にします
        read_only_fields = ('user', 'duration', 'created_at', 'user_username')



# health_records/serializers.py

# ... (既存のHealthRecordSerializer) ...

class SleepSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepSession
        fields = '__all__'
        read_only_fields = ('user', 'sleep_score') # ユーザーとスコアは自動で設定