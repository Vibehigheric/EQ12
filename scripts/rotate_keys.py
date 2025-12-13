import os
import requests
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("KeyRotator")

# Load environment variables
load_dotenv()

def check_odds_api(key):
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f"ODDS_API_KEY {key[:4]}... is VALID.")
            return True
        else:
            logger.error(f"ODDS_API_KEY {key[:4]}... is INVALID. Status: {response.status_code}, Body: {response.text}")
            return False
    except Exception as e:
        logger.error(f"ODDS_API_KEY check failed: {e}")
        return False

def check_openweather_api(key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q=London&appid={key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f"OPENWEATHER_API_KEY {key[:4]}... is VALID.")
            return True
        else:
            logger.error(f"OPENWEATHER_API_KEY {key[:4]}... is INVALID. Status: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"OPENWEATHER_API_KEY check failed: {e}")
        return False

def blacklist_key(key_name):
    """Comments out the invalid key in .env"""
    env_path = ".env"
    try:
        with open(env_path, "r") as f:
            lines = f.readlines()
        
        with open(env_path, "w") as f:
            for line in lines:
                if line.startswith(f"{key_name}="):
                    f.write(f"# BLACKLISTED {line}")
                    logger.info(f"Blacklisted {key_name} in .env")
                else:
                    f.write(line)
    except Exception as e:
        logger.error(f"Failed to blacklist key {key_name}: {e}")

def main():
    logger.info("Starting API Key Rotation Check...")
    
    # Check ODDS_API_KEY
    odds_key = os.getenv("ODDS_API_KEY")
    if odds_key:
        if not check_odds_api(odds_key):
            blacklist_key("ODDS_API_KEY")
    else:
        logger.warning("ODDS_API_KEY not found in environment.")

    # Check OPENWEATHER_API_KEY
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    if weather_key:
        if not check_openweather_api(weather_key):
            blacklist_key("OPENWEATHER_API_KEY")
    else:
        logger.warning("OPENWEATHER_API_KEY not found in environment.")

    logger.info("Key Rotation Check Complete.")

if __name__ == "__main__":
    main()
