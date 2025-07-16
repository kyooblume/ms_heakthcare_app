# recipes/urls.py

from django.urls import path
from .views import SuggestRecipeView

urlpatterns = [
    path('suggestions/', SuggestRecipeView.as_view(), name='recipe-suggestions'),
]