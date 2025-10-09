from django.urls import path
from . import views

urlpatterns = [
    path('meals/analyze', views.analyze_meal, name='analyze-meal'),
    path('meals', views.meals, name='meals'),
    path('meals/<int:pk>', views.meal_detail, name='meal-detail'),
    path('meals/daily', views.daily_summary, name='daily-summary'),
]