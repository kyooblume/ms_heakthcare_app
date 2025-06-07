from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User # Django標準のUserモデル
from rest_framework import generics
from rest_framework.permissions import AllowAny # 認証なしでアクセス許可
from .serializers import UserRegistrationSerializer # 先ほど作成したシリアライザーをインポート
from rest_framework.permissions import AllowAny, IsAuthenticated 
from .serializers import UserRegistrationSerializer, UserProfileSerializer
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