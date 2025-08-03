# recipes/urls.py

from django.urls import path
from .views import SuggestRecipeView, DinnerSuggestionView

urlpatterns = [
    path('suggestions/', SuggestRecipeView.as_view(), name='recipe-suggestions'),
    path('suggest-dinner/', DinnerSuggestionView.as_view(), name='suggest-dinner'),
]