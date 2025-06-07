# accounts/urls.py
from django.urls import path
from .views import UserRegistrationView, UserProfileView

app_name = 'accounts'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]