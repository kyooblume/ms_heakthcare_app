from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User # Django標準のUserモデル
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated 
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework import viewsets
from .models import UserDevice
from .serializers import UserDeviceSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PasswordChangeSerializer
from rest_framework.views import APIView
# ↓ 睡眠アンケートのモデルをインポート
from health_records.models import SleepChronotypeSurvey 
# from django.contrib.auth.models import User # 既存のビューでインポート済みのはず
# --- ★ここを修正 ---
# UserProfileモデルと、対応するシリアライザーをインポートします
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserRegistrationView(generics.CreateAPIView):
    """
    新しいユーザーを作成するためのビュー。
    誰でもアクセス可能（認証不要）。
    """
    queryset = User.objects.all() # CreateAPIViewでは必須だが、このビューでは直接的には使われない
    permission_classes = (AllowAny,) # このAPIエンドポイントへのアクセス許可設定。ユーザー登録なので誰でも許可。
    serializer_class = UserRegistrationSerializer # このビューがデータの検証と作成に使用するシリアライザーを指定



class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    認証されたユーザー自身のプロフィールを取得・更新するためのビュー。
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated] # 認証されたユーザーのみアクセス可能


    
    def get_object(self):
        # ユーザーに紐づくプロフィールを取得、なければ作成
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def partial_update(self, request, *args, **kwargs):
        # PATCHリクエスト（部分更新）の処理
        instance = self.get_object()
        
        # --- ★ここから修正 ---
        # Big Fiveの回答がすべて送られてきたかチェック
        big5_fields = ['big5_openness', 'big5_conscientiousness', 'big5_extraversion', 'big5_agreeableness', 'big5_neuroticism']
        
        # もしリクエストデータにBig Fiveの必須項目がすべて含まれていたら、
        # オンボーディング完了とみなして、リクエストデータにフラグを追加する
        if all(field in request.data for field in big5_fields):
            request.data['onboarding_complete'] = True
        # --- ★ここまで修正 ---

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

# --- ★ここから新しい UserDeviceViewSet を追加 ---
class UserDeviceViewSet(viewsets.ModelViewSet):
    """
    ユーザーのデバイスを管理するためのAPIビュー。
    - 自分のデバイスの一覧取得 (GET)
    - 新しいデバイスの登録 (POST)
    - 特定のデバイスの登録解除 (DELETE)
    """
    serializer_class = UserDeviceSerializer
    permission_classes = [IsAuthenticated] # 認証されたユーザーのみアクセス可能

    def get_queryset(self):
        # 自分のデバイスだけを返すようにする
        return UserDevice.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 新しいデバイスを登録する際に、現在のユーザーを自動的に紐付ける
        # また、同じデバイストークンが既に存在する場合は、持ち主を更新する (再インストール対応など)
        serializer.save(user=self.request.user)


# --- ★ここから新しい PasswordChangeView を追加 ---
class PasswordChangeView(APIView):
    """
    パスワード変更用のAPIビュー
    """
    permission_classes = [IsAuthenticated] # 認証されたユーザーのみアクセス可能

    def post(self, request, *args, **kwargs):
        # context={'request': request} を渡すことで、シリアライザー内でrequest.userが使えるようになる
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"detail": "パスワードが正常に変更されました。"}, status=status.HTTP_200_OK)
        # is_validでエラーが出た場合は、自動的に400エラーが返される



# accounts/views.py
# ... (既存のインポート文に以下を追加・確認) ...
from rest_framework.views import APIView
from datetime import date

# ... (既存のビューはそのまま) ...

# --- ★ここから新しいビューを追加 ---
class RecommendedIntakeView(APIView):
    """
    ユーザーのプロフィール情報に基づき、推奨される1日の栄養摂取量を計算して返す。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile = request.user.profile

        # 計算に必要な情報が揃っているかチェック
        required_fields = [profile.date_of_birth, profile.gender, profile.target_weight, profile.height_cm, profile.activity_level]
        if not all(required_fields):
            return Response(
                {"error": "目標計算には、生年月日、性別、体重、身長、活動レベルのプロフィール情報が全て必要です。"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. 年齢を計算
        today = date.today()
        age = today.year - profile.date_of_birth.year - ((today.month, today.day) < (profile.date_of_birth.month, profile.date_of_birth.day))

        # 2. BMR（基礎代謝量）を計算（ハリス・ベネディクト方程式改良版）
        if profile.gender == 'male':
            bmr = 88.362 + (13.397 * profile.target_weight) + (4.799 * profile.height_cm) - (5.677 * age)
        elif profile.gender == 'female':
            bmr = 447.593 + (9.247 * profile.target_weight) + (3.098 * profile.height_cm) - (4.330 * age)
        else: # 性別が 'other' または未設定の場合、平均的な値を用いるなどの工夫が可能
            bmr = 66.5 + (13.75 * profile.target_weight) + (5.003 * profile.height_cm) - (6.775 * age) # ここでは男性の式を代用

        # 3. TDEE（1日の総消費カロリー）を計算
        tdee = bmr * profile.activity_level

        # 4. PFCバランスから各栄養素のグラム数を計算（例: P20%, F25%, C55%）
        # タンパク質と炭水化物は4kcal/g, 脂質は9kcal/g
        protein_g = (tdee * 0.20) / 4
        fat_g = (tdee * 0.25) / 9
        carb_g = (tdee * 0.55) / 4
        
        # レスポンスデータを作成
        response_data = {
            "calculated_targets": {
                "calories": round(tdee),
                "protein": round(protein_g, 1),
                "fat": round(fat_g, 1),
                "carbohydrate": round(carb_g, 1)
            },
            "based_on": {
                "age": age,
                "gender": profile.gender,
                "height_cm": profile.height_cm,
                "weight_kg": profile.target_weight,
                "activity_level": profile.activity_level
            }
        }
        
        return Response(response_data)
    

class UserOnboardingStatusView(APIView):
    """
    ユーザーのオンボーディングと各アンケートの回答状況を返すビュー。
    フロントエンドは、このAPIの結果を見て次に表示する画面を判断する。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # get_or_createを使って、プロフィールが存在しない場合でもエラーにならないようにする
        profile, created = UserProfile.objects.get_or_create(user=user)

        # 睡眠アンケートに回答済みかチェック
        sleep_survey_completed = SleepChronotypeSurvey.objects.filter(user=user).exists()

        # big5_opennessが空(None)かどうかで、BigFiveに回答済みか判断
        big5_survey_completed = profile.big5_openness is not None

        response_data = {
            'onboarding_completed': profile.onboarding_complete,
            'needs_big5_survey': not big5_survey_completed,
            'needs_sleep_survey': not sleep_survey_completed
        }

        return Response(response_data, status=status.HTTP_200_OK)