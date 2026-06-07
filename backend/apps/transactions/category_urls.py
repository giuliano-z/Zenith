"""Ruta del listado de categorías. Se monta bajo /api/categories/ en config/urls.py.

Vive en la app transactions porque el modelo Category pertenece a este módulo
(RF-014); no amerita una app propia para un único endpoint read-only.
"""
from django.urls import path

from apps.transactions.views import CategoryListView

app_name = "categories"

urlpatterns = [
    path("", CategoryListView.as_view(), name="category-list"),  # RF-014
]
