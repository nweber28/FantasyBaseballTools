from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .models import ESPNService

# Create your views here.
def player_table(request):
    players = ESPNService.fetch_player_data()
    players = players[:100]
    return JsonResponse({'players': players})