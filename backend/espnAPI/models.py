"""
Service for interacting with ESPN Fantasy Baseball API.
"""
import requests
from django.db import models
import logging
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple

from backend.settings import cookies, DEFAULT_LEAGUE_ID

logger = logging.getLogger(__name__)

class ESPNService:
    """Service for interacting with ESPN Fantasy Baseball API."""
    
    BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb"
    
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
    
    @staticmethod
    def fetch_team_rosters(league_id: str = DEFAULT_LEAGUE_ID, cookies: dict = cookies, season_id: int = 2025) -> Optional[Dict[str, Any]]:
        """
        Fetch team rosters for a specific league.
        
        Args:
            league_id: The ESPN league ID
            season_id: The season ID to fetch data for
            
        Returns:
            Dictionary of team rosters or None if request fails
        """
        url = f"{ESPNService.BASE_URL}/seasons/{season_id}/segments/0/leagues/{league_id}?view=mRoster"
        
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
            logger.info(f"Fetching ESPN team rosters for league {league_id}")
            response = requests.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()
            data = response.json()
            
            if 'teams' in data:
                logger.info(f"Successfully fetched roster data with {len(data['teams'])} teams")
            else:
                logger.warning(f"Roster data missing 'teams' key. Keys: {list(data.keys())}")
                
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ESPN team rosters: {e}\n\n")
            return None
        

    @staticmethod
    def fetch_league_draft_data(cookies: dict = cookies, season_id: int = 2025, league_id: str = DEFAULT_LEAGUE_ID) -> Optional[Dict[str, Any]]:
        """
        Fetch all player data from ESPN.
        
        Args:
            season_id: The season ID to fetch data for
            
        Returns:
            Dictionary of player data or None if request fails
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
            return draft_picks        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ESPN draft data: {e}\n\n")
            return []