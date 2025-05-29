"""
Open WebUI Sports Score Plugin
Tracks scores for Duke, UNC, USC (Gamecocks), and Clemson
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from pydantic import BaseModel, Field


class Manifest(BaseModel):
    """Plugin manifest"""
    id: str = "sports_score_tracker"
    name: str = "Sports Score Tracker"
    version: str = "1.0.0"
    required_open_webui_version: str = "0.3.0"
    description: str = "Track live scores and updates for Duke, UNC, USC Gamecocks, and Clemson"
    icon: str = "🏀"
    author: str = "Your Name"
    author_url: str = "https://github.com/yourusername"
    funding_url: str = "https://github.com/sponsors/yourusername"
    license: str = "MIT"


class Tools:
    def __init__(self):
        self.team_mapping = {
            150: "Duke Blue Devils",
            153: "UNC Tar Heels", 
            2579: "USC Gamecocks",
            228: "Clemson Tigers"
        }
        
        self.team_abbreviations = {
            150: "DUKE",
            153: "UNC",
            2579: "USC",
            228: "CLEM"
        }

    async def get_team_games(self, sport: str = "basketball", league: str = "mens-college-basketball") -> List[Dict]:
        """Get games for tracked teams"""
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._filter_team_games(data)
                    else:
                        return []
        except Exception as e:
            print(f"Error fetching {sport} games: {e}")
            return []

    def _filter_team_games(self, data: Dict) -> List[Dict]:
        """Filter games for our tracked teams"""
        team_games = []
        tracked_ids = set(str(tid) for tid in self.team_mapping.keys())
        
        for event in data.get('events', []):
            for competition in event.get('competitions', []):
                competitors = competition.get('competitors', [])
                
                # Check if any of our teams are playing
                for competitor in competitors:
                    if competitor['team']['id'] in tracked_ids:
                        # Format the game data
                        game_info = self._format_game_info(event, competition)
                        if game_info:
                            team_games.append(game_info)
                        break
        
        return team_games

    def _format_game_info(self, event: Dict, competition: Dict) -> Optional[Dict]:
        """Format game information for display"""
        try:
            status = event.get('status', {})
            competitors = competition.get('competitors', [])
            
            if len(competitors) != 2:
                return None
                
            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
            
            game_info = {
                'id': event.get('id'),
                'name': event.get('name', ''),
                'date': event.get('date'),
                'status': {
                    'type': status.get('type', {}).get('name', 'Unknown'),
                    'state': status.get('type', {}).get('state', 'Unknown'),
                    'detail': status.get('type', {}).get('detail', ''),
                    'short_detail': status.get('type', {}).get('shortDetail', '')
                },
                'home_team': {
                    'id': home_team['team']['id'],
                    'name': home_team['team']['displayName'],
                    'abbreviation': home_team['team']['abbreviation'],
                    'score': home_team.get('score', '0'),
                    'record': home_team.get('records', [{}])[0].get('summary', '') if home_team.get('records') else ''
                },
                'away_team': {
                    'id': away_team['team']['id'],
                    'name': away_team['team']['displayName'],
                    'abbreviation': away_team['team']['abbreviation'],
                    'score': away_team.get('score', '0'),
                    'record': away_team.get('records', [{}])[0].get('summary', '') if away_team.get('records') else ''
                },
                'venue': competition.get('venue', {}).get('fullName', ''),
                'broadcast': ', '.join([b.get('names', [''])[0] for b in competition.get('broadcasts', [])])
            }
            
            return game_info
            
        except Exception as e:
            print(f"Error formatting game info: {e}")
            return None

    def _format_games_display(self, games: List[Dict], sport_name: str) -> str:
        """Format games for display"""
        if not games:
            return f"No {sport_name} games found for tracked teams."
        
        output = [f"\n🏀 **{sport_name.upper()} GAMES** 🏀\n"]
        
        for game in games:
            status = game['status']
            home = game['home_team']
            away = game['away_team']
            
            # Determine if any of our teams are playing
            our_teams = []
            if home['id'] in [str(tid) for tid in self.team_mapping.keys()]:
                our_teams.append(home['abbreviation'])
            if away['id'] in [str(tid) for tid in self.team_mapping.keys()]:
                our_teams.append(away['abbreviation'])
            
            teams_indicator = f"📍 {', '.join(our_teams)}" if our_teams else ""
            
            # Format score display
            if status['state'] in ['in', 'post']:
                score_display = f"{away['abbreviation']} {away['score']} - {home['score']} {home['abbreviation']}"
            else:
                score_display = f"{away['abbreviation']} @ {home['abbreviation']}"
            
            # Status display
            status_display = status['short_detail'] or status['detail']
            
            game_display = f"""
**{score_display}** {teams_indicator}
📅 {status_display}
🏟️ {game['venue']}
📺 {game['broadcast'] if game['broadcast'] else 'TBD'}
"""
            output.append(game_display)
        
        return '\n'.join(output)

    async def get_live_scores(
        self,
        __user__: dict,
        sport: str = "both"
    ) -> str:
        """
        Get live scores for tracked teams (Duke, UNC, USC Gamecocks, Clemson)
        
        Args:
            sport: "basketball", "football", or "both" (default: "both")
        """
        results = []
        
        if sport in ["basketball", "both"]:
            bball_games = await self.get_team_games("basketball", "mens-college-basketball")
            if bball_games:
                results.append(self._format_games_display(bball_games, "Basketball"))
        
        if sport in ["football", "both"]:
            football_games = await self.get_team_games("football", "college-football")
            if football_games:
                results.append(self._format_games_display(football_games, "Football"))
        
        if not results:
            return f"No games found for tracked teams in {sport}."
        
        return '\n\n'.join(results)

    async def get_team_schedule(
        self,
        __user__: dict,
        team: str,
        days: int = 7
    ) -> str:
        """
        Get upcoming schedule for a specific team
        
        Args:
            team: Team name (duke, unc, usc, clemson)
            days: Number of days to look ahead (default: 7)
        """
        team_lower = team.lower()
        team_id = None
        
        # Map team names to IDs
        name_mapping = {
            'duke': 150,
            'unc': 153,
            'usc': 2579,
            'clemson': 228
        }
        
        if team_lower in name_mapping:
            team_id = name_mapping[team_lower]
        else:
            return f"Team '{team}' not found. Available teams: duke, unc, usc, clemson"
        
        # Get current and upcoming games
        all_games = []
        
        # Check both sports
        for sport, league in [("basketball", "mens-college-basketball"), ("football", "college-football")]:
            games = await self.get_team_games(sport, league)
            for game in games:
                if (game['home_team']['id'] == str(team_id) or 
                    game['away_team']['id'] == str(team_id)):
                    game['sport'] = sport
                    all_games.append(game)
        
        if not all_games:
            return f"No games found for {self.team_mapping[team_id]}"
        
        # Sort by date
        all_games.sort(key=lambda x: x['date'])
        
        output = [f"\n📅 **{self.team_mapping[team_id].upper()} SCHEDULE** 📅\n"]
        
        for game in all_games:
            sport_emoji = "🏀" if game['sport'] == "basketball" else "🏈"
            home = game['home_team']
            away = game['away_team']
            
            # Determine opponent
            if home['id'] == str(team_id):
                opponent = f"vs {away['abbreviation']}"
                location = "Home"
            else:
                opponent = f"@ {home['abbreviation']}"
                location = "Away"
            
            status = game['status']['short_detail'] or game['status']['detail']
            
            game_display = f"""
{sport_emoji} **{opponent}** ({location})
📅 {status}
🏟️ {game['venue']}
📺 {game['broadcast'] if game['broadcast'] else 'TBD'}
"""
            output.append(game_display)
        
        return '\n'.join(output)

    async def get_team_info(
        self,
        __user__: dict,
        team: str = "all"
    ) -> str:
        """
        Get information about tracked teams
        
        Args:
            team: Specific team name or "all" for all teams (default: "all")
        """
        if team.lower() == "all":
            output = ["🏀🏈 **TRACKED TEAMS** 🏈🏀\n"]
            for team_id, team_name in self.team_mapping.items():
                abbrev = self.team_abbreviations[team_id]
                output.append(f"• **{team_name}** ({abbrev}) - ID: {team_id}")
            output.append("\nUse commands like: get_live_scores, get_team_schedule duke")
            return '\n'.join(output)
        else:
            # Individual team info could be expanded here
            return f"Individual team info for {team} - feature coming soon!"


# Plugin entry point
def get_tools():
    return Tools()