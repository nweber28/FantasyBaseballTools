"""
Service for interacting with ESPN Fantasy Baseball API.
"""
import requests
from django.db import models
import logging
import json
import sqlite3
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple

from backend.settings import cookies, DEFAULT_LEAGUE_ID

logger = logging.getLogger(__name__)

class DraftPick(models.Model):
    keeper = models.BooleanField(default=False)
    player_id = models.IntegerField()
    round_id = models.IntegerField()
    round_pick_number = models.IntegerField()
    fantasy_team_id = models.IntegerField()
    overall_pick_number = models.IntegerField()

    def __str__(self):
        return "Player Id " + str(self.player_id) + ", Pick #" + str(self.overall_pick_number)
    
    @classmethod
    def create(cls, keeper, player_id, round_id, round_pick_number, fantasy_team_id, overall_pick_number):
        draft_pick = cls(keeper=keeper, 
                         player_id=player_id, 
                         round_id=round_id, 
                         round_pick_number=round_pick_number, 
                         fantasy_team_id=fantasy_team_id, 
                         overall_pick_number=overall_pick_number)
        return draft_pick
    

class Player(models.Model):
    player_id = models.IntegerField()
    player_name = models.CharField(max_length=50)
    player_points = models.IntegerField()
    fantasy_team_id = models.IntegerField(default=0) # if not on team currently
    position_id = models.IntegerField(default=0)
    pro_team = models.IntegerField(default=0)

    def __str__(self):
        return self.player_name
    
    @classmethod
    def create(cls, player_id, player_name, player_points, fantasy_team_id, position_id, pro_team):
        player = cls(player_id=player_id, 
                         player_name=player_name, 
                         player_points=player_points, 
                         fantasy_team_id=fantasy_team_id, 
                         position_id=position_id,
                         pro_team=pro_team)
        return player


# static methods used to interact with ESPNAPI
class ESPNService:
    """Service for interacting with ESPN Fantasy Baseball API."""
    
    # Utility Functions
    @staticmethod
    def get_applied_total(stats_list: List[Dict[str, Any]], target_year: int = 2025) -> float:
        """
        Extract the appliedTotal from a player's stats where statSplitTypeId == 0 and seasonId == target_year.

        Args:
            stats_list: List of stats dictionaries
            target_year: Season year to match

        Returns:
            The appliedTotal value or 0 if not found
        """
        for stat in stats_list:
            if stat.get("seasonId") == target_year and stat.get("statSplitTypeId") == 0:
                return stat.get("appliedTotal", 0)
        return 0

    # Common URL for all calls
    BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb"
    
    # Fetches all players rostered and non-rostered
    @staticmethod
    def fetch_player_data(cookies: dict = cookies, season_id: int = 2025) -> Optional[Dict[str, Any]]:
        """
        Fetch all player data from ESPN.
        
        Args:
            season_id: The season ID to fetch data for
            
        Returns:
            Dictionary of player data or None if request fails
        """
        url = f"{ESPNService.BASE_URL}/seasons/{season_id}/players?scoringPeriodId=0&view=players_wl&view=kona_player_info"
        logger.info(f"Full url: " + url)
        
        headers = {
            "X-Fantasy-Filter": '{"filterActive":{"value":true}}',
            "sec-ch-ua-platform": "macOS",
            "Referer": "https://fantasy.espn.com/",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "X-Fantasy-Platform": "kona-PROD-ea1dac81fac83846270c371702992d3a2f69aa70",
            "sec-ch-ua-mobile": "?0",
            "X-Fantasy-Source": "kona",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        try:
            logger.info("\n\nFetching ESPN player data")
            response = requests.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched ESPN player data: {len(data)} players\n\n")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ESPN data: {e}\n\n")
            return []
    
    # returns basic team data, abbreviations, small json call
    @staticmethod
    def fetch_teams_data(league_id: str = DEFAULT_LEAGUE_ID, cookies: dict = cookies, season_id: int = 2025) -> Optional[Dict[str, Any]]:
        """
        Fetch teams data for a specific league.
        
        Args:
            league_id: The ESPN league ID
            season_id: The season ID to fetch data for
            
        Returns:
            Dictionary of teams data or None if request fails
        """
        url = f"{ESPNService.BASE_URL}/seasons/{season_id}/segments/0/leagues/{league_id}"
        
        headers = {
            "sec-ch-ua-platform": "macOS",
            "Referer": "https://fantasy.espn.com/",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "X-Fantasy-Platform": "kona-PROD-ea1dac81fac83846270c371702992d3a2f69aa70",
            "sec-ch-ua-mobile": "?0",
            "X-Fantasy-Source": "kona",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        try:
            logger.info(f"\n\nFetching ESPN teams data for league {league_id}")
            response = requests.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched ESPN teams data: {len(data.get('teams', []))} teams\n\n")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ESPN teams data: {e}\n\n")
            return None
    
    # all draft data from given year
    @staticmethod
    def fetch_league_draft_data(cookies: dict = cookies, season_id: int = 2025, league_id: str = DEFAULT_LEAGUE_ID) -> Optional[Dict[str, Any]]:
        """
        Fetch all draft data from ESPN.
        
        Args:
            season_id: The season ID to fetch data for
            cookies: swid and espn2
            league_id: id of fantasy league
            
        Returns:
            Dictionary of draft data or None if request fails
        Base URL
            https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb

        Rest of URL
            /seasons/2025/segments/0/leagues/league_id?view=mDraftDetail&view=mSettings&view=mTeam&view=modular&view=mNav
                    ^^season_id    ^^ not sure ^^league_id
        """

        url = f"{ESPNService.BASE_URL}/seasons/{season_id}/segments/0/leagues/{league_id}?view=mDraftDetail"
        logger.info(f"Full url: " + url)
        
        headers  = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        }
        
        try:
            logger.info("Fetching ESPN draft picks data")
            response = requests.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Draft response keys: {list(data.keys())}")
            draft_picks = data.get("draftDetail", {}).get("picks", [])
            logger.info(f"Successfully fetched {len(draft_picks)} draft picks")

            # Save to Draft Picks model

            for pick in draft_picks:
                draftPick = DraftPick.create(
                    pick.get("reservedForKeeper"),
                    pick.get("playerId"),
                    pick.get("roundId"),
                    pick.get("roundPickNumber"),
                    pick.get("teamId"),
                    pick.get("overallPickNumber")
                    )
                draftPick.save()

            logger.info(f"Successfully created {len(draft_picks)} DraftPicks objects")

            return draft_picks        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ESPN draft data: {e}\n\n")
            return []

    # fetches all rostered player data
    @staticmethod
    def fetch_player_points_data(cookies: dict = cookies, season_id: int = 2025, league_id: str = DEFAULT_LEAGUE_ID) -> Optional[Dict[str, Any]]:
        """
        Fetch all player points data from ESPN.
        Would be ideal to do this just for drafted players to start.
        May expand to all players rostered at some point or another in the future.
        
        Args:
            season_id: The season ID to fetch data for
            cookies: swid and espn2
            league_id: id of fantasy league
            
        Returns:
            Dictionary of draft data or None if request fails
        Base URL
        https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/

        Rest of URL
        seasons/2025/segments/0/leagues/1310196412?view=mRoster

        """

        url = f"{ESPNService.BASE_URL}/seasons/{season_id}/segments/0/leagues/{league_id}?&view=mRoster"
        logger.info(f"Full url: " + url)
        
        headers  = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        }
        
        try:
            logger.info("Fetching ESPN player points data")
            response = requests.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Points response keys: {list(data.keys())}")
            teams = data.get("teams", {})
            logger.info(f"Successfully fetched {len(teams)} teams")
            
            # group players by team
            team_players = []
            create_operations = 0
            update_operations = 0

            for team in teams:
                team_id = team.get("id")
                
                players = []
                for entry in team.get("roster", {}).get("entries", []):
                    player = entry.get("playerPoolEntry", {})

                    apiPoints = ESPNService.get_applied_total(entry.get("playerPoolEntry", {}).get("player", {}).get("stats", []), season_id)
                    apiPlayerId = player.get("id")
                    apiPlayerName = player.get("player", {}).get("fullName")
                    apiPlayerPosition = player.get("player", {}).get("defaultPositionId")
                    apiPlayerProTeam = player.get("player", {}).get("proTeamId")

                    players.append({
                        "id": apiPlayerId,
                        "fullName": apiPlayerName,
                        "position": apiPlayerPosition,
                        "proTeam": apiPlayerProTeam,
                        "points": apiPoints
                    })

                    # save or update player record
                    player_id_val = player.get("id")
                    if Player.objects.filter(player_id=player_id_val).exists():
                        # player exists, update record
                        dbPlayer = Player.objects.filter(player_id=player_id_val).first()
                        if dbPlayer:
                            dbPlayer.player_points = apiPoints
                            dbPlayer.position_id = apiPlayerPosition
                            dbPlayer.pro_team = apiPlayerProTeam
                            update_operations += 1
                        else:
                            logger.warning(f"Expected player with player_id = {player_id_val} but none was found")
                    else:
                        # player does not exist, create new record
                        dbPlayer = Player.create(apiPlayerId,
                                      apiPlayerName,
                                      apiPoints,
                                      team_id,
                                      apiPlayerPosition,
                                      apiPlayerProTeam)
                        dbPlayer.save()
                        create_operations += 1
                
                team_players.append({
                    "teamId": team_id,
                    "players": players
                })

                #logger.info("Team players: %s", json.dumps(team_players, indent=2))
                logger.info(f"Successfully fetched team")
            
            logger.info(f"Successfully created " + str(create_operations) + " player records")
            logger.info(f"Successfully updated " + str(update_operations) + " player records")

            return team_players        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ESPN player points data: {e}\n\n")
            return []
