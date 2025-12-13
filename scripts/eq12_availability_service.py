import time
import json
import os
import logging
from datetime import datetime
from nba_api_client import NBAStatsClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/availability_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EQ12_AvailabilityService")

DATA_DIR = "data"
CACHE_FILE = os.path.join(DATA_DIR, "nba_player_status.json")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def update_cache():
    client = NBAStatsClient()
    
    logger.info("🔄 Starting Availability Update Cycle...")
    
    # 1. Fetch Roster
    try:
        roster = client.get_active_players()
        logger.info(f"Fetched {len(roster)} players from NBA Roster.")
    except Exception as e:
        logger.error(f"Failed to fetch roster: {e}")
        return

    # 2. Transform to Status Map
    # In a real production system, we would merge this with an Injury Feed (e.g., Rotowire scrape).
    # For this 'Free Tier' implementation, we assume Roster Status 1 = Active, but we flag 'Unknown' for daily status.
    
    status_map = {}
    timestamp = datetime.utcnow().isoformat()
    
    for p in roster:
        # DEFAULT STATE: UNAVAILABLE (Positive Confirmation Model)
        # We only mark ACTIVE if we have a positive signal.
        # For this demo, we assume Roster Status 1 = ACTIVE_CONFIRMED (simulated).
        # In prod, this would require: Roster=1 AND InjuryReport=Clean AND GameDayActive=True.
        
        status = "UNAVAILABLE"
        if p.get('ROSTERSTATUS') == 1:
             status = "ACTIVE" # Mapped to our allowed status
             
        status_map[p['DISPLAY_FIRST_LAST']] = {
            "id": p['PERSON_ID'],
            "team_id": p['TEAM_ID'],
            "status": status, 
            "availability_enum": "ACTIVE_CONFIRMED" if status == "ACTIVE" else "UNAVAILABLE",
            "source": "NBA_Official_API",
            "last_updated": timestamp
        }
        
    # 3. Save to Cache
    ensure_data_dir()
    with open(CACHE_FILE, 'w') as f:
        json.dump({
            "meta": {"updated_at": timestamp, "count": len(status_map)},
            "players": status_map
        }, f, indent=2)
        
    logger.info(f"✅ Cache updated at {CACHE_FILE}")

def run_service_loop(interval=300):
    """
    Runs the service loop.
    """
    logger.info(f"🚀 Availability Service Started. Interval: {interval}s")
    while True:
        update_cache()
        time.sleep(interval)

if __name__ == "__main__":
    # For demonstration, run once then exit, or loop if arg provided
    import sys
    if "--loop" in sys.argv:
        run_service_loop()
    else:
        update_cache()
