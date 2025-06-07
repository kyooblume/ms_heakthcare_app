# health_records/serializers.py

from rest_framework import serializers
from .models import HealthRecord
# from django.contrib.auth.models import User # Userモデルを直接参照する場合に備えてコメントアウト

class HealthRecordSerializer(serializers.ModelSerializer):
    # user フィールドは、APIレスポンスでユーザー名を表示するようにカスタマイズする例
    # source='user.username' は、HealthRecordモデルのuserフィールドの先のusername属性を参照します。
    # read_only=True なので、このシリアライザー経由でuserフィールドを書き換えることはできません。
    # (ユーザーの割り当てはビュー側で行います)
    user_username = serializers.CharField(source='user.username', read_only=True)

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
            'notes'
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