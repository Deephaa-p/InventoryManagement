from django.contrib import admin
from django.urls import path, include
from .views import LoginView, RegisterView, CategoryListCreateView, ItemListCreateView, ItemDetailView, AddRemoveStockView, InventorySummary

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('categories', CategoryListCreateView.as_view(), name='categories'),
    path('inventory', ItemListCreateView.as_view()),
    path('inventory/<int:pk>', ItemDetailView.as_view()),
    path('inventory/add-remove-stock', AddRemoveStockView.as_view()),
    path('inventory/summary', InventorySummary.as_view()),
]