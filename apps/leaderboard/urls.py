from django.urls import path
from .views import leaderboard_views

urlpatterns = [
    path('', leaderboard_views)
]