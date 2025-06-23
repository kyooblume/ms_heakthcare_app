# chat/views.py
import google.generativeai as genai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# settings.py からAPIキーを読み込んで設定
# もしキーが設定されていなければ、エラーにならないようにtry-exceptで囲む
try:
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
except AttributeError:
    pass 

class ChatView(APIView):
    """
    チャットボットと会話するためのAPIビュー
    """
    permission_classes = [IsAuthenticated] # ログインしているユーザーのみ利用可能

    def post(self, request, *args, **kwargs):
        # フロントエンドから送られてきたメッセージを取得
        user_message = request.data.get('message')

        if not user_message:
            return Response({"error": "メッセージがありません。"}, status=status.HTTP_400_BAD_REQUEST)
        
        # APIキーが設定されているか確認
        if not settings.GEMINI_API_KEY:
             return Response({"error": "AIサービスのAPIキーが設定されていません。"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # 使用するAIモデルを初期化
            model = genai.GenerativeModel('gemini-pro')
            
            # AIにメッセージを送信して応答を生成
            # ここでプロンプトを工夫することで、AIの振る舞いをカスタマイズできます
            prompt = f"あなたは親切なヘルスケアアシスタントです。ユーザーの次の質問に簡潔に答えてください：{user_message}"
            response = model.generate_content(prompt)
            
            # AIからのテキスト応答を返す
            return Response({'response': response.text}, status=status.HTTP_200_OK)

        except Exception as e:
            # もしAPI呼び出しでエラーが起きた場合
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)