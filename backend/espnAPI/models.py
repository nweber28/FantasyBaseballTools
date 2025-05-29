"""
Service for interacting with ESPN Fantasy Baseball API.
"""
import requests
from django.db import models, transaction
from django.utils import timezone

import logging
import traceback

import pandas as pd
import numpy as np
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Dict, Any, Optional, List, Tuple

from backend.settings import cookies, DEFAULT_LEAGUE_ID
from backend.constants import KEEPER_PICK_VALUE

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
    last_updated = models.DateTimeField(default=timezone.now)
    currently_rostered = models.BooleanField(default=False)
    draft_metric = models.DecimalField(default=0.0, max_digits=9, decimal_places=3)

    def __str__(self):
        return self.player_name
    
    @classmethod
    def create(cls, player_id, player_name, player_points, fantasy_team_id, position_id, pro_team, currently_rostered=False):
        player = cls(player_id=player_id, 
                         player_name=player_name, 
                         player_points=player_points, 
                         fantasy_team_id=fantasy_team_id, 
                         position_id=position_id,
                         pro_team=pro_team,
                         currently_rostered=currently_rostered)
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

    # Calculates draft metric column for each drafted player
    @staticmethod
    def calculate_draft_metric():
        """
        Given: 

        Problems: Players that are not rostered wont be returned from fetch_player_points_data,
                    Account for players that were dropped, waivers, traded, etc.

        Returns: Updated Draft Metric column
        
        """
        # For each drafted player returned by player points data
        # And for drafted players not currently rostered, may just send these to the void
            # put these on separate list/table
        # Create Points scored scale using pandas


        # Collect all draft/ data
        #draft_picks = DraftPick.objects.all()
        #all_players = Player.objects.all()


        # Collect rostered player data

        #dropped_draft_picks = []

        # Join with points data for found players

        # 4 groups: drafted and currently rostered, --> player id in draft_picks and all_players, accounted for
            #       drafted but not currently rostered, --> player id in draft_picks but not in currently_rostered, may not be in Players model, if so will be 0.0
            #       not drafted but currently rostered, --> player id not in draft_picks but in currently_rostered, will be given 0.0
            #       not drafted and not currently rostered, --> player id not in draft_picks, but may be in Player model, will be given 0.0

        # Logic for drafted + currently rostered players
        logger.info(f"\nCalculating Draft Metrics\n")
        
        # Create DataFrames from Player and DraftPick models
        players_df = pd.DataFrame(
            Player.objects.values("id", "player_id", "player_points")
        )
        draft_df = pd.DataFrame(
            DraftPick.objects.values("player_id", "overall_pick_number", "keeper")
        )

        # Replace overall_pick_number with KEEPER_CONSTANT for keepers
        draft_df.loc[draft_df["keeper"] == True, "overall_pick_number"] = KEEPER_PICK_VALUE

        # Calculate percentiles
        players_df["points_percentile"] = players_df["player_points"].rank(pct=True)
        draft_df["draft_percentile"] = draft_df["overall_pick_number"].rank(pct=True)

        # Map player id to both percentiles, merged only contains drafted, currently rostered players
        merged = pd.merge(players_df, draft_df, on="player_id", how="inner")

        # Calculate the metric, replace nan vals with 0.0 if any
        merged["draft_metric"] = (
            merged["points_percentile"] / (merged["draft_percentile"] ** 2)
        ).replace([np.inf, -np.inf], np.nan)
        merged["draft_metric"] = merged["draft_metric"].fillna(0.0)

        # Map player id to their draft metric score
        metric_map = dict(zip(merged["id"], merged["draft_metric"]))

        try:
            # Ensures that if one value fails, no values are updated
            with transaction.atomic():
                for player in Player.objects.filter(id__in=metric_map.keys()):
                    value = Decimal(metric_map[player.id]).quantize(Decimal("0.001"), rounding=ROUND_DOWN)
                    player.draft_metric = value
                    player.save()
            logger.info(f"Successfully saved draft metric data")
            return 0
        except Exception as e:
            logger.warning(f"\nError saving draft metric data: {e}\n{traceback.format_exc()}")


        # create metric for all groups

        # if drafted player is not found in Player model (current or former), create player record for them
            # this is for players who were drafted and dropped before this app was made

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

                    # save or update player record
                    player_id_val = player.get("id")
                    if Player.objects.filter(player_id=player_id_val).exists():
                        # player exists, update record
                        dbPlayer = Player.objects.filter(player_id=player_id_val).first()
                        if dbPlayer:
                            dbPlayer.player_points = apiPoints
                            dbPlayer.position_id = apiPlayerPosition
                            dbPlayer.pro_team = apiPlayerProTeam
                            dbPlayer.currently_rostered = True
                            dbPlayer.last_updated = timezone.now
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
                                      apiPlayerProTeam,
                                      True)
                        dbPlayer.save()
                        create_operations += 1
                
                    players.append({
                        "id": apiPlayerId,
                        "fullName": apiPlayerName,
                        "position": apiPlayerPosition,
                        "proTeam": apiPlayerProTeam,
                        "points": apiPoints
                    })

                team_players.append({
                    "teamId": team_id,
                    "players": players
                })

                #logger.info("Team players: %s", json.dumps(team_players, indent=2))
                logger.info(f"Successfully fetched team")
            
            logger.info(f"Successfully created " + str(create_operations) + " player records")
            logger.info(f"Successfully updated " + str(update_operations) + " player records")

            # Calculate draft metric
            ESPNService.calculate_draft_metric()

            return team_players        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ESPN player points data: {e}\n\n")
            return []
