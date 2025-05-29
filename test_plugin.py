#!/usr/bin/env python3
"""
Test script for Sports Score Tracker plugin
"""

import asyncio
import json
from main import Tools

async def test_plugin():
    """Test the sports score tracker plugin functions"""
    tools = Tools()
    
    print("🏀 Testing Sports Score Tracker Plugin 🏀\n")
    
    # Test get_team_info
    print("1. Testing get_team_info...")
    team_info = await tools.get_team_info({}, "all")
    print(team_info)
    print("\n" + "="*50 + "\n")
    
    # Test get_live_scores for basketball
    print("2. Testing get_live_scores (basketball)...")
    basketball_scores = await tools.get_live_scores({}, "basketball")
    print(basketball_scores)
    print("\n" + "="*50 + "\n")
    
    # Test get_live_scores for football
    print("3. Testing get_live_scores (football)...")
    football_scores = await tools.get_live_scores({}, "football")
    print(football_scores)
    print("\n" + "="*50 + "\n")
    
    # Test get_live_scores for NFL
    print("4. Testing get_live_scores (NFL)...")
    nfl_scores = await tools.get_live_scores({}, "nfl")
    print(nfl_scores)
    print("\n" + "="*50 + "\n")
    
    # Test get_team_schedule for Duke
    print("5. Testing get_team_schedule (Duke)...")
    duke_schedule = await tools.get_team_schedule({}, "duke", 14)
    print(duke_schedule)
    print("\n" + "="*50 + "\n")
    
    # Test get_team_schedule for Panthers
    print("6. Testing get_team_schedule (Panthers)...")
    panthers_schedule = await tools.get_team_schedule({}, "panthers", 14)
    print(panthers_schedule)
    print("\n" + "="*50 + "\n")
    
    print("✅ Plugin testing completed!")

if __name__ == "__main__":
    asyncio.run(test_plugin())