# chat/urls.py
from django.urls import path
from .views import ChatView

app_name = 'chat'

urlpatterns = [
    path('conversation/', ChatView.as_view(), name='chat-conversation'),
]