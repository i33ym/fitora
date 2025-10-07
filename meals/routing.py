from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/meals/analyze/', consumers.MealAnalysisConsumer.as_asgi()),
]