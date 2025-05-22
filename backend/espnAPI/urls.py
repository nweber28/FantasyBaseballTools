from django.urls import path
from . import views

urlpatterns = [
    path('players/', views.player_table, name='player_table'),
    path('draft/', views.draft_table, name='draft_table'),
    path('points/', views.player_points_table, name='player_points_table'),
]
