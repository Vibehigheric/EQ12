import os
import logging
from typing import List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("KeyManager")

class KeyManager:
    def __init__(self, env_path: str = ".env"):
        self.env_path = env_path
        load_dotenv(self.env_path)
        self.blacklisted_keys = set()
        self.keys = {
            "ODDS_API": [os.getenv("ODDS_API_KEY"), os.getenv("THE_ODDS_API_KEY")],
            "OPENWEATHER": [os.getenv("OPENWEATHER_API_KEY")],
            "OPENAI": [os.getenv("OPENAI_API_KEY"), os.getenv("AZURE_OPENAI_API_KEY")],
            "GROQ": [os.getenv("GROQ_API_KEY")],
            "CLAUDE": [os.getenv("CLAUDE_API_KEY")],
            "GOOGLE": [os.getenv("GOOGLE_AI_API_KEY")],
            "HUGGINGFACE": [os.getenv("HUGGINGFACE_TOKEN")],
            "GITHUB": [os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_TOKEN_2"), os.getenv("GITHUB_MODELS_TOKEN")]
        }
        # Remove None values and duplicates
        for service in self.keys:
            self.keys[service] = list(set([k for k in self.keys[service] if k]))

    def get_key(self, service_name: str) -> Optional[str]:
        """Returns the first non-blacklisted key for the service."""
        if service_name not in self.keys:
            logger.warning(f"Service {service_name} not found in KeyManager.")
            return None
        
        for key in self.keys[service_name]:
            if key not in self.blacklisted_keys:
                return key
        
        logger.error(f"No valid keys available for {service_name}.")
        return None

    def report_failure(self, service_name: str, key: str):
        """Reports a key failure, blacklists it in memory, and comments it out in .env."""
        logger.warning(f"Reporting failure for {service_name} key: {key[:4]}...")
        self.blacklisted_keys.add(key)
        self._blacklist_in_file(key)

    def _blacklist_in_file(self, key_to_blacklist: str):
        """Comments out the key in the .env file."""
        try:
            with open(self.env_path, "r") as f:
                lines = f.readlines()
            
            with open(self.env_path, "w") as f:
                for line in lines:
                    if key_to_blacklist in line and not line.strip().startswith("#"):
                        f.write(f"# BLACKLISTED_AUTO {line}")
                        logger.info(f"Blacklisted key in {self.env_path}")
                    else:
                        f.write(line)
        except Exception as e:
            logger.error(f"Failed to update .env file: {e}")

    def get_free_api_fallback(self, service_name: str) -> Optional[str]:
        """Returns a free API endpoint if available."""
        if service_name == "OPENWEATHER":
            return "https://api.weather.gov" # NWS API
        return None
