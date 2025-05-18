from django.shortcuts import render, HttpResponse
from .models import ESPNService

# Create your views here.
def player_table(request):
    playerData = ESPNService.fetch_player_data()
    return render(request, 'players/player_table.html', {'players': playerData})
