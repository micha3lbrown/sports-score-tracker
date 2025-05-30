# Sports Score Tracker Plugin for Open WebUI

A plugin for tracking live scores and schedules for college teams (Duke Blue Devils, UNC Tar Heels, USC Gamecocks, Clemson Tigers) and NFL teams (Carolina Panthers, Jacksonville Jaguars, Chicago Bears, Atlanta Falcons).

## Features

- 🏀 Live basketball scores and game status
- 🏈 Live college football and NFL scores and game status  
- 📅 Team schedules and upcoming games
- 📊 Real-time updates from ESPN API
- 🎯 Focused on ACC teams + USC Gamecocks + select NFL teams

## Installation

### For Open WebUI
See [OPEN_WEBUI_SETUP.md](OPEN_WEBUI_SETUP.md) for detailed installation instructions.

**Quick setup:**
1. Go to Open WebUI Admin Panel → Functions → Add Function
2. Copy/paste the contents of `openwebui_function.py`
3. Save and enable the function
4. Select "Sports Score Tracker" from the model dropdown and chat naturally

### Docker Demo (Local Testing)
```bash
# Clone the repository
git clone https://github.com/micha3lbrown/sports-score-tracker.git
cd sports-score-tracker

# Build and run with Docker Compose
docker-compose up

# Or run specific demos:
docker-compose --profile demo up demo-teams
docker-compose --profile demo up demo-scores
docker-compose --profile demo up demo-nfl

# Run the full test suite
docker-compose --profile test up test

# Interactive mode
docker-compose run --rm sports-tracker python demo.py teams
docker-compose run --rm sports-tracker python demo.py scores nfl
docker-compose run --rm sports-tracker python demo.py schedule panthers 14
```

### Manual Installation
```bash
pip install -r requirements.txt
python test_plugin.py
```

## Usage

### Available Functions

#### `get_live_scores(sport="both")`
Get current live scores for tracked teams.

**Parameters:**
- `sport`: "basketball", "football", "nfl", or "both" (default)

**Examples:**
```
get_live_scores("basketball")
get_live_scores("nfl")
get_live_scores("both")
```

#### `get_team_schedule(team, days=7)`
Get upcoming schedule for a specific team.

**Parameters:**
- `team`: College teams: "duke", "unc", "usc", "clemson" or NFL teams: "panthers", "jaguars", "bears", "falcons" (required)
- `days`: Number of days to look ahead (default: 7)

**Examples:**
```
get_team_schedule("duke", 14)
get_team_schedule("panthers", 7)
```

#### `get_team_info(team="all")`
Get information about tracked teams.

**Parameters:**
- `team`: Specific team name or "all" for all teams (default: "all")

**Example:**
```
get_team_info("all")
```

## Testing

Run the test script to verify plugin functionality:

```bash
python test_plugin.py
```

## Teams Tracked

### College Teams
- **Duke Blue Devils** (DUKE) - Basketball & Football
- **UNC Tar Heels** (UNC) - Basketball & Football  
- **USC Gamecocks** (USC) - Basketball & Football
- **Clemson Tigers** (CLEM) - Basketball & Football

### NFL Teams
- **Carolina Panthers** (CAR) - Football
- **Jacksonville Jaguars** (JAX) - Football
- **Chicago Bears** (CHI) - Football
- **Atlanta Falcons** (ATL) - Football

## Technical Details

- Uses ESPN's public API for real-time sports data
- Async/await support for non-blocking operations
- Pydantic models for data validation
- Error handling for API failures

## Requirements

- Python 3.8+
- aiohttp>=3.8.0
- pydantic>=1.10.0
- Open WebUI 0.3.0+

## License

MIT License