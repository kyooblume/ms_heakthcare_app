"""
URL configuration for backend_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# backend_project/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # 管理画面用のURL
    path('admin/', admin.site.urls),

    # 私たちが作成したAPI用のURL
    path('api/accounts/', include('accounts.urls')),
    path('api/auth/', include('accounts.urls', namespace='accounts')),
    path('api/health/', include('health_records.urls', namespace='health_records')),
    path('api/meals/', include('meals.urls', namespace='meals')),
    path('api/chat/', include('chat.urls')),
    path('api/reports/', include('reports.urls', namespace='reports')), 
    path('api/products/', include('products.urls')), # ← ★この行を追加
    path('api/', include('surveys.urls')), 
    path('api/recipes/', include('recipes.urls')),
    # トークン認証用のURL
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]