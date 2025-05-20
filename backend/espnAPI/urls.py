from django.urls import path
from . import views

urlpatterns = [
    path('players/', views.player_table, name='player_table'),
]
