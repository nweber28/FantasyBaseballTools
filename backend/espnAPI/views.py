from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .models import ESPNService

# Create your views here.
def player_table(request):
    players = ESPNService.fetch_player_data()
    players = players[:100]
    return JsonResponse({'players': players})

# Create your views here.
def draft_table(request):
    draftPicks = ESPNService.fetch_league_draft_data()
    #draftPicks = draftPicks[:100]
    return JsonResponse({'draftPicks': draftPicks})

def player_points_table(request):
    playerPoints = ESPNService.fetch_player_points_data()
    playerPoints = playerPoints[:100]
    return JsonResponse({'playerPoints': playerPoints})