## chat/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import os
import openai

# .envファイルからAPIキーを読み込み、OpenAIクライアントを設定
try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    IS_OPENAI_CONFIGURED = True
except Exception as e:
    # APIキーが設定されていないなどの場合に備える
    print(f"OpenAIの初期化エラー: {e}")
    IS_OPENAI_CONFIGURED = False

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not IS_OPENAI_CONFIGURED:
            return Response({"error": "サーバーでOpenAI APIが設定されていません。"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        user_message = request.data.get('message')

        if not user_message:
            return Response({"error": "メッセージがありません。"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # --- ★ここが「マスコットの性格」を決める指示書（プロンプト）です！ ---
            completion = client.chat.completions.create(
                model="gpt-4o",  # または "gpt-3.5-turbo"
                messages=[
                    {
                        "role": "system", 
                        "content": "あなたは、ユーザーの健康をサポートするヘルスケアアプリの公式マスコット『』です。元気で、ユーザーに常に寄り添い、ポジティブな言葉で励ましてください。栄養学や運動に関する知識も豊富ですが、難しい言葉は使わず、誰にでも分かるように、楽しく伝えてください。"
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ]
            )
            
            ai_response = completion.choices[0].message.content
            return Response({"reply": ai_response})

        except Exception as e:
            return Response({"error": f"APIとの通信中にエラーが発生しました: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)