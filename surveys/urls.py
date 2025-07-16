# surveys/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurveyViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r'surveys', SurveyViewSet, basename='survey')
router.register(r'answers', AnswerViewSet, basename='answer')

urlpatterns = [
    path('', include(router.urls)),
]