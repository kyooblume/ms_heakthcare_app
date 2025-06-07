from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User # Django標準のUserモデル
from rest_framework import generics
from rest_framework.permissions import AllowAny # 認証なしでアクセス許可
from .serializers import UserRegistrationSerializer # 先ほど作成したシリアライザーをインポート
from rest_framework.permissions import AllowAny, IsAuthenticated 
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework import viewsets
from .models import UserDevice
from .serializers import UserDeviceSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PasswordChangeSerializer
# from django.contrib.auth.models import User # 既存のビューでインポート済みのはず

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
        # URLにIDを含める代わりに、リクエストしてきたユーザーのプロフィールを返す
        # self.request.user で現在ログインしているユーザーが取得できる
        # .profile は、UserProfileモデルの related_name='profile' で設定したもの
        return self.request.user.profile
    


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