# products/serializers.py

from rest_framework import serializers
from .models import ProductNutrition

class ProductNutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductNutrition
        fields = '__all__'