from django.urls import path
from . import views
from .views import PlayerList


urlpatterns = [
    path('players/', views.player_table, name='player_table'),
    path('draft/', views.draft_table, name='draft_table'),
    path('points/', views.player_points_table, name='player_points_table'),
    path('calculate-draft-metrics/', views.calculate_draft_metric, name='calculate_draft_metric'),
    path('api/playerData/', PlayerList.as_view(), name='entry-list'),
]
