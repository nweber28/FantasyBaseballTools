from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .models import ESPNService, Player, DraftPick
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PlayerSerializer

# Create your views here.
def draft_table(request):
    draftPicks = ESPNService.fetch_league_draft_data()
    #draftPicks = draftPicks[:100]
    return JsonResponse({'draftPicks': draftPicks})

def player_points_table(request):
    playerPoints = ESPNService.fetch_player_points_data()
    playerPoints = playerPoints[:100]
    return JsonResponse({'playerPoints': playerPoints})

@csrf_exempt
def calculate_draft_metric(request):
    ESPNService.calculate_draft_metric()
    return JsonResponse({"status": "success", "message": "Metrics calculated"})

class PlayerList(APIView):
    def get(self, request):
        players = Player.objects.filter(currently_rostered = True)
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)
    