# Installing Sports Score Tracker in Open WebUI

## Quick Setup

### 1. Download Plugin Files
```bash
# Option A: Clone the repository
git clone https://github.com/micha3lbrown/sports-score-tracker.git
cd sports-score-tracker

# Option B: Download just the plugin files
curl -O https://raw.githubusercontent.com/micha3lbrown/sports-score-tracker/main/openwebui_function.py
```

### 2. Install in Open WebUI

#### Method 1: Admin Panel (Recommended)
1. Open your Open WebUI instance
2. Go to **Admin Panel** → **Settings** → **Functions**
3. Click **"+ Add Function"**
4. Copy and paste the entire contents of `openwebui_function.py` into the function editor
5. Click **"Save"** - Open WebUI will automatically install dependencies
6. Enable the function if it's not already enabled

#### Method 2: File Upload
1. In Open WebUI Admin Panel → **Functions**
2. Click **"Import Function"**
3. Upload `openwebui_function.py`
4. Enable the function

#### Method 3: Manual Installation
1. Copy `openwebui_function.py` to your Open WebUI functions directory:
   ```bash
   # Default path (adjust for your installation)
   cp openwebui_function.py /path/to/open-webui/backend/apps/webui/routers/functions/
   ```
2. Restart Open WebUI

### 3. Install Dependencies
Open WebUI should automatically install dependencies from the manifest, but if needed:
```bash
pip install aiohttp>=3.8.0 pydantic>=1.10.0 requests>=2.25.0
```

## Using the Plugin

Once installed, you can use these functions in any Open WebUI chat:

### Available Functions

#### `get_live_scores`
Get current live scores for your teams:
```
get_live_scores()              # All sports
get_live_scores("nfl")         # NFL only
get_live_scores("basketball")  # College basketball only
get_live_scores("football")    # College football only
```

#### `get_team_schedule`
Get upcoming games for a specific team:
```
get_team_schedule("panthers")     # Panthers next 7 days
get_team_schedule("duke", 14)     # Duke next 14 days
get_team_schedule("falcons", 30)  # Falcons next 30 days
```

#### `get_team_info`
Show all tracked teams:
```
get_team_info()               # All teams
get_team_info("all")          # Same as above
```

### Example Chat Usage

**You:** "Show me the latest NFL scores for our teams"
**AI:** *[calls get_live_scores("nfl")]*
> 🏈 **NFL GAMES** 🏈
> 
> **CAR @ JAX** 📍 JAX, CAR
> 📅 9/7 - 1:00 PM EDT
> 🏟️ EverBank Stadium
> 📺 FOX

**You:** "When does Duke play next?"
**AI:** *[calls get_team_schedule("duke")]*
> 📅 **DUKE BLUE DEVILS SCHEDULE** 📅
> 
> 🏈 **vs ELON** (Home) (College)
> 📅 TBD
> 🏟️ Wallace Wade Stadium

## Tracked Teams

### College Teams
- **Duke Blue Devils** - `duke`
- **UNC Tar Heels** - `unc` 
- **USC Gamecocks** - `usc`
- **Clemson Tigers** - `clemson`

### NFL Teams  
- **Carolina Panthers** - `panthers` or `carolina`
- **Jacksonville Jaguars** - `jaguars` or `jacksonville`
- **Chicago Bears** - `bears` or `chicago`
- **Atlanta Falcons** - `falcons` or `atlanta`

## Troubleshooting

### Plugin Not Showing Up
1. Check Open WebUI logs for errors
2. Verify dependencies are installed
3. Restart Open WebUI service
4. Check function permissions in Admin Panel

### API Errors
- Plugin uses ESPN's public API (no key required)
- Check internet connectivity
- If ESPN API is down, wait and try again

### Function Call Issues
- Make sure function names match exactly: `get_live_scores`, `get_team_schedule`, `get_team_info`
- Team names are case-insensitive
- If you get "No Function class found", make sure you copied the entire `openwebui_function.py` file
- The plugin requires a `Pipe`, `Filter`, or `Action` class for Open WebUI compatibility

## Advanced Configuration

### Custom Teams
To add different teams, modify the team mappings in `main.py`:
```python
# Find ESPN team IDs at: https://site.api.espn.com/apis/site/v2/sports/
self.nfl_team_mapping = {
    29: "Carolina Panthers",
    # Add your team here with ESPN ID
}
```

### Scheduling Updates
The plugin fetches live data on each call. For automatic updates, you could:
1. Set up a cron job to call the functions
2. Use Open WebUI's scheduling features (if available)
3. Create a workflow that calls the functions periodically

## Docker Development
For testing changes locally:
```bash
git clone https://github.com/micha3lbrown/sports-score-tracker.git
cd sports-score-tracker
docker-compose up
```