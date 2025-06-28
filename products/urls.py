# products/urls.py

from django.urls import path
from .views import ProductLookupView

app_name = 'products'

urlpatterns = [
    path('lookup/<str:barcode>/', ProductLookupView.as_view(), name='product-lookup'),
]