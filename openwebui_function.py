"""
title: Sports Score Tracker
author: Michael Brown
date: 2024-05-28
version: 1.0
license: MIT
description: Track live scores for Duke, UNC, USC Gamecocks, Clemson, Panthers, Jaguars, Bears, Falcons
requirements: aiohttp
"""

import aiohttp
from typing import Dict, List, Optional, Generator
from pydantic import BaseModel, Field


class Pipe:
    class Valves(BaseModel):
        MODEL_ID: str = Field(default="sports-tracker", description="Model identifier for the sports tracker")
        
    def __init__(self):
        self.type = "manifold"
        self.id = "sports-tracker"
        self.name = "Sports Score Tracker"
        self.valves = self.Valves()
        
        # College teams
        self.college_teams = {
            150: "Duke Blue Devils",
            153: "UNC Tar Heels", 
            2579: "USC Gamecocks",
            228: "Clemson Tigers"
        }
        
        # NFL teams
        self.nfl_teams = {
            29: "Carolina Panthers",
            30: "Jacksonville Jaguars", 
            3: "Chicago Bears",
            1: "Atlanta Falcons"
        }
        
        # Combined teams for lookup
        self.all_teams = {**self.college_teams, **self.nfl_teams}
        
        # Team name mappings
        self.team_lookup = {
            'duke': 150, 'unc': 153, 'usc': 2579, 'clemson': 228,
            'panthers': 29, 'carolina': 29, 'jaguars': 30, 'jacksonville': 30,
            'bears': 3, 'chicago': 3, 'falcons': 1, 'atlanta': 1
        }

    def get_models(self):
        return [
            {
                "id": "sports-tracker",
                "name": "Sports Score Tracker",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai"
            }
        ]

    async def pipe(self, body: dict) -> Generator[str, None, None]:
        """
        Main pipe function that processes sports score requests
        """
        try:
            # Extract the user's message
            messages = body.get("messages", [])
            if not messages:
                yield "Please ask me about sports scores, schedules, or team information!"
                return
                
            last_message = messages[-1].get("content", "").lower()
            
            # Determine what the user wants based on their message
            if any(word in last_message for word in ["help", "what can you do", "commands"]):
                response = self._get_help()
            elif "teams" in last_message or "who do" in last_message or "track" in last_message:
                response = self._get_team_info()
            elif "schedule" in last_message:
                team = self._extract_team_from_message(last_message)
                if team:
                    response = await self._get_team_schedule(team)
                else:
                    response = "Please specify a team: duke, unc, usc, clemson, panthers, jaguars, bears, or falcons"
            elif "nfl" in last_message and "score" in last_message:
                response = await self._get_live_scores("nfl")
            elif "basketball" in last_message:
                response = await self._get_live_scores("basketball")
            elif ("football" in last_message and "college" in last_message) or "college football" in last_message:
                response = await self._get_live_scores("football")
            elif "score" in last_message or "game" in last_message:
                response = await self._get_live_scores("both")
            else:
                # Default response with suggestions
                response = self._get_help()
            
            # Stream the response
            yield response
            
        except Exception as e:
            yield f"Sorry, I encountered an error: {str(e)}"

    def _get_help(self) -> str:
        """Get help information"""
        return """🏀🏈 **Sports Score Tracker** 🏈🏀

I can help you with:
• **Live Scores**: "Show me the latest scores" or "NFL scores"
• **Team Schedules**: "When does Duke play next?" or "Panthers schedule"  
• **Team Info**: "What teams do you track?"

**Tracked Teams:**
• College: Duke, UNC, USC Gamecocks, Clemson
• NFL: Panthers, Jaguars, Bears, Falcons

Just ask me naturally about any team or sport!"""

    def _extract_team_from_message(self, content: str) -> Optional[str]:
        """Extract team name from user message"""
        for team_name in self.team_lookup.keys():
            if team_name in content:
                return team_name
        return None

    def _get_team_info(self) -> str:
        """Get information about tracked teams"""
        output = ["🏀🏈 **TRACKED TEAMS** 🏈🏀\n"]
        
        output.append("**College Teams:**")
        for team_id, team_name in self.college_teams.items():
            output.append(f"• **{team_name}** - ID: {team_id}")
        
        output.append("\n**NFL Teams:**")
        for team_id, team_name in self.nfl_teams.items():
            output.append(f"• **{team_name}** - ID: {team_id}")
        
        output.append(f"\n**Usage Examples:**")
        output.append("• 'Show me NFL scores'")
        output.append("• 'When does Duke play next?'")
        output.append("• 'Panthers schedule'")
        
        return "\n".join(output)

    async def _get_live_scores(self, sport: str = "both") -> str:
        """Get live scores for tracked teams"""
        try:
            results = []
            
            if sport in ["basketball", "both"]:
                games = await self._fetch_games("basketball", "mens-college-basketball")
                if games:
                    results.append(f"🏀 **COLLEGE BASKETBALL** 🏀\n{self._format_games(games)}")
            
            if sport in ["football", "both"]:
                games = await self._fetch_games("football", "college-football")
                if games:
                    results.append(f"🏈 **COLLEGE FOOTBALL** 🏈\n{self._format_games(games)}")
            
            if sport in ["nfl", "both"]:
                games = await self._fetch_games("football", "nfl")
                if games:
                    results.append(f"🏈 **NFL** 🏈\n{self._format_games(games)}")
            
            if not results:
                return f"No games found for tracked teams in {sport} right now."
            
            return "\n\n".join(results)
            
        except Exception as e:
            return f"Error fetching scores: {str(e)}"

    async def _get_team_schedule(self, team: str, days: int = 14) -> str:
        """Get upcoming schedule for a specific team"""
        try:
            team_id = self.team_lookup.get(team.lower())
            if not team_id:
                return f"Team '{team}' not found. Available: {', '.join(self.team_lookup.keys())}"
            
            team_name = self.all_teams[team_id]
            
            # Determine which leagues to check
            leagues = []
            if team_id in self.college_teams:
                leagues = [("basketball", "mens-college-basketball"), ("football", "college-football")]
            else:
                leagues = [("football", "nfl")]
            
            all_games = []
            for sport, league in leagues:
                games = await self._fetch_games(sport, league)
                for game in games:
                    if (game['home_team']['id'] == str(team_id) or 
                        game['away_team']['id'] == str(team_id)):
                        game['sport'] = sport
                        all_games.append(game)
            
            if not all_games:
                return f"No upcoming games found for {team_name}"
            
            output = [f"📅 **{team_name.upper()} SCHEDULE** 📅\n"]
            for game in all_games:
                sport_emoji = "🏀" if game['sport'] == "basketball" else "🏈"
                home = game['home_team']
                away = game['away_team']
                
                if home['id'] == str(team_id):
                    opponent = f"vs {away['abbreviation']}"
                    location = "Home"
                else:
                    opponent = f"@ {home['abbreviation']}"
                    location = "Away"
                
                status = game['status'].get('short_detail', game['status'].get('detail', 'TBD'))
                venue = game.get('venue', 'TBD')
                broadcast = game.get('broadcast', '')
                
                game_line = f"{sport_emoji} **{opponent}** ({location})\n📅 {status}\n🏟️ {venue}"
                if broadcast:
                    game_line += f"\n📺 {broadcast}"
                
                output.append(game_line + "\n")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"Error fetching schedule: {str(e)}"

    async def _fetch_games(self, sport: str, league: str) -> List[Dict]:
        """Fetch games from ESPN API"""
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._filter_team_games(data)
                    return []
        except Exception:
            return []

    def _filter_team_games(self, data: Dict) -> List[Dict]:
        """Filter games for tracked teams"""
        team_games = []
        tracked_ids = set(str(tid) for tid in self.all_teams.keys())
        
        for event in data.get('events', []):
            for competition in event.get('competitions', []):
                competitors = competition.get('competitors', [])
                
                # Check if any tracked teams are playing
                for competitor in competitors:
                    if competitor['team']['id'] in tracked_ids:
                        game_info = self._format_game_info(event, competition)
                        if game_info:
                            team_games.append(game_info)
                        break
        
        return team_games

    def _format_game_info(self, event: Dict, competition: Dict) -> Optional[Dict]:
        """Format game information"""
        try:
            status = event.get('status', {})
            competitors = competition.get('competitors', [])
            
            if len(competitors) != 2:
                return None
                
            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
            
            return {
                'home_team': {
                    'id': home_team['team']['id'],
                    'name': home_team['team']['displayName'],
                    'abbreviation': home_team['team']['abbreviation'],
                    'score': home_team.get('score', '0')
                },
                'away_team': {
                    'id': away_team['team']['id'],
                    'name': away_team['team']['displayName'],
                    'abbreviation': away_team['team']['abbreviation'],
                    'score': away_team.get('score', '0')
                },
                'status': {
                    'state': status.get('type', {}).get('state', 'Unknown'),
                    'detail': status.get('type', {}).get('detail', ''),
                    'short_detail': status.get('type', {}).get('shortDetail', '')
                },
                'venue': competition.get('venue', {}).get('fullName', ''),
                'broadcast': ', '.join([b.get('names', [''])[0] for b in competition.get('broadcasts', [])])
            }
        except Exception:
            return None

    def _format_games(self, games: List[Dict]) -> str:
        """Format games for display"""
        if not games:
            return "No games found."
        
        output = []
        for game in games:
            home = game['home_team']
            away = game['away_team']
            status = game['status']
            
            # Check if our teams are playing
            our_teams = []
            tracked_ids = set(str(tid) for tid in self.all_teams.keys())
            if home['id'] in tracked_ids:
                our_teams.append(home['abbreviation'])
            if away['id'] in tracked_ids:
                our_teams.append(away['abbreviation'])
            
            teams_indicator = f" 📍 {', '.join(our_teams)}" if our_teams else ""
            
            # Format score/matchup
            if status['state'] in ['in', 'post']:
                matchup = f"**{away['abbreviation']} {away['score']} - {home['score']} {home['abbreviation']}**"
            else:
                matchup = f"**{away['abbreviation']} @ {home['abbreviation']}**"
            
            status_text = status.get('short_detail') or status.get('detail', 'TBD')
            venue = game.get('venue', 'TBD')
            broadcast = game.get('broadcast', '')
            
            game_text = f"{matchup}{teams_indicator}\n📅 {status_text}\n🏟️ {venue}"
            if broadcast:
                game_text += f"\n📺 {broadcast}"
            
            output.append(game_text)
        
        return "\n\n".join(output)