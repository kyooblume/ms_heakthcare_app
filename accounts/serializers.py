from django.contrib.auth.models import User  # Django標準のUserモデルを使います
from django.contrib.auth.password_validation import validate_password # Django標準のパスワードバリデーション
from rest_framework import serializers
from .models import UserProfile , UserDevice  # 作成したUserProfileとUserDeviceモデルをインポート

class UserRegistrationSerializer(serializers.ModelSerializer):
    # パスワードは書き込み専用にし、入力時には表示されるが、APIのレスポンスには含めない
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password], # Djangoのパスワード強度チェックを利用
        style={'input_type': 'password'} # APIドキュメントでパスワード入力欄のように表示
    )
    # パスワード確認用のフィールド
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm password' # APIドキュメントでの表示名
    )
    # emailは必須項目にする
    email = serializers.EmailField(required=True)

    class Meta:
        model = User  # どのモデルをベースにするか指定 (今回はDjango標準のUserモデル)
        # APIでやり取りするフィールドを指定
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False}, # 任意項目にする場合
            'last_name': {'required': False}   # 任意項目にする場合
        }

    def validate(self, attrs):
        # attrsは送られてきたデータ全体 (username, email, password, password2など)
        # passwordとpassword2が一致するかチェック
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password fields didn't match."})
        return attrs # 問題なければデータをそのまま返す

    def create(self, validated_data):
        # validated_dataには、validateメソッドでチェック済みのデータが入っている
        # password2はユーザー作成には不要なので取り除く
        validated_data.pop('password2')

        # User.objects.create_user() を使うことで、パスワードが適切にハッシュ化される
        user = User.objects.create_user(**validated_data)
        # User.objects.create_user(
        #     username=validated_data['username'],
        #     email=validated_data['email'],
        #     password=validated_data['password'],
        #     first_name=validated_data.get('first_name', ''), # 任意項目のためgetで取得
        #     last_name=validated_data.get('last_name', '')    # 任意項目のためgetで取得
        # )
        return user
    

    
    
# --- ★ここから新しい UserProfileSerializer を追加 ---
class UserProfileSerializer(serializers.ModelSerializer):
    # ユーザー名も一緒に表示したいので、読み取り専用フィールドとして追加
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile # UserProfileモデルと連携
        # APIで表示・編集したいフィールドを指定
        fields = [
            'username',
            'date_of_birth', 
            'gender', 
            'target_weight', 
            'target_steps_per_day',
            'target_calories', 
            'target_protein', 
            'target_fat', 
            'target_carbohydrate',
            'onboarding_complete',
            'big5_openness', 
            'big5_conscientiousness',
            'big5_extraversion',
            'big5_agreeableness',
            'big5_neuroticism',
            'onboarding_complete',
        ]


# --- ★ここから新しい UserDeviceSerializer を追加 ---
class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        # APIでやり取りするフィールドを指定します
        fields = ['id', 'device_token', 'platform', 'is_active', 'created_at']
        # このうち、クライアントから送ってもらうのは device_token と platform だけです。
        # user はビューでリクエストから自動設定します。
        read_only_fields = ['id', 'user', 'is_active', 'created_at']


# accounts/serializers.py

# ... (既存のインポート文や他のシリアライザーはそのまま) ...
from django.contrib.auth import password_validation

# --- ★ここから新しい PasswordChangeSerializer を追加 ---
class PasswordChangeSerializer(serializers.Serializer):
    """
    パスワード変更用のシリアライザー
    """
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password1 = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate_old_password(self, value):
        # 現在のパスワードが正しいか検証
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("現在のパスワードが正しくありません。")
        return value

    def validate(self, data):
        # 新しいパスワードが2つとも一致するか検証
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({"new_password2": "新しいパスワードが一致しません。"})

        # Django標準のパスワード強度バリデーションを実行
        password_validation.validate_password(data['new_password1'], self.context['request'].user)

        return data

    def save(self, **kwargs):
        # パスワードを更新
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user