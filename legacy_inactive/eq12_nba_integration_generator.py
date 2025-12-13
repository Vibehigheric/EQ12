#!/usr/bin/env python3
"""
EQ12 NBA Data Sources Integration Helper
Automatically integrates NBA data sources into your production collector
"""

import json
import sys
from pathlib import Path

def generate_integration_code():
    """Generate Python code to integrate NBA data sources"""
    
    integration_template = '''
# NBA Data Sources Integration for EQ12 Production Collector
# Auto-generated from nba_data_sources.json

import requests
import asyncio
import aiohttp
from datetime import datetime

class NBADataSourceManager:
    def __init__(self):
        self.sources = self.load_sources()
        self.session = None
    
    def load_sources(self):
        """Load NBA data sources configuration"""
        config_path = Path("C:/EQ12/configs/nba_data_sources.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config['data_sources']
    
    async def initialize_session(self):
        """Initialize async HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close async HTTP session"""
        if self.session:
            await self.session.close()
    
    async def fetch_nba_api_data(self):
        """Fetch data from nba_api (GitHub client)"""
        # Use nba_api Python client for official NBA.com data
        try:
            from nba_api.stats.endpoints import leaguegamefinder
            from nba_api.stats.endpoints import teamgamelog
            
            # Get recent games
            games = leaguegamefinder.LeagueGameFinder(
                season_nullable='2024-25',
                season_type_nullable='Regular Season'
            ).get_data_frames()[0]
            
            return games.head(10).to_dict('records')
        except ImportError:
            print(" nba_api not installed. Run: pip install nba_api")
            return []
        except Exception as e:
            print(f" NBA API error: {e}")
            return []
    
    async def fetch_balldontlie_data(self):
        """Fetch data from Ball Don't Lie API"""
        url = "https://www.balldontlie.io/api/v1/games"
        params = {
            'seasons[]': 2024,
            'per_page': 10
        }
        
        try:
            if not self.session:
                await self.initialize_session()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                else:
                    print(f" Ball Don't Lie API error: {response.status}")
                    return []
        except Exception as e:
            print(f" Ball Don't Lie fetch error: {e}")
            return []
    
    async def fetch_espn_data(self):
        """Fetch data from ESPN unofficial API"""
        url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        
        try:
            if not self.session:
                await self.initialize_session()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('events', [])
                else:
                    print(f" ESPN API error: {response.status}")
                    return []
        except Exception as e:
            print(f" ESPN fetch error: {e}")
            return []
    
    async def collect_all_free_sources(self):
        """Collect data from all free NBA sources"""
        print(" Collecting from free NBA data sources...")
        
        await self.initialize_session()
        
        try:
            # Collect from multiple sources concurrently
            nba_data = await self.fetch_nba_api_data()
            balldontlie_data = await self.fetch_balldontlie_data()
            espn_data = await self.fetch_espn_data()
            
            results = {
                'timestamp': datetime.utcnow().isoformat(),
                'sources': {
                    'nba_api': {
                        'count': len(nba_data),
                        'data': nba_data
                    },
                    'balldontlie': {
                        'count': len(balldontlie_data),
                        'data': balldontlie_data
                    },
                    'espn': {
                        'count': len(espn_data),
                        'data': espn_data
                    }
                }
            }
            
            print(f" NBA API: {len(nba_data)} records")
            print(f" Ball Don't Lie: {len(balldontlie_data)} records")
            print(f" ESPN: {len(espn_data)} records")
            
            return results
            
        finally:
            await self.close_session()
    
    def get_core_apis(self):
        """Get list of core API sources"""
        return [s for s in self.sources 
                if s.get('type') == 'api' 
                and s.get('integration_level') == 'core']
    
    def get_free_apis(self):
        """Get list of free API sources"""
        return [s for s in self.sources 
                if s.get('type') == 'api' 
                and not s.get('auth_required')]

# Integration example
async def main():
    """Main integration test"""
    manager = NBADataSourceManager()
    
    print(" Available core APIs:")
    for api in manager.get_core_apis()[:5]:
        auth_status = "" if api.get('auth_required') else ""
        print(f"    {api['name']} {auth_status}")
    
    print("\\n Free APIs ready for use:")
    for api in manager.get_free_apis()[:5]:
        print(f"    {api['name']}: {api['url']}")
    
    # Test data collection
    print("\\n Testing data collection...")
    results = await manager.collect_all_free_sources()
    
    # Save results
    results_path = Path("C:/EQ12/logs/nba_data_sources_test.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f" Results saved to: {results_path}")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    return integration_template

def create_integration_file():
    """Create the integration helper file"""
    integration_code = generate_integration_code()
    
    integration_path = Path("C:/EQ12/scripts/eq12_nba_sources_integration.py")
    with open(integration_path, 'w', encoding='utf-8') as f:
        f.write(integration_code)
    
    print(f" Integration helper created: {integration_path}")
    return integration_path

if __name__ == "__main__":
    print(" EQ12 NBA Data Sources Integration Generator")
    print("=" * 60)
    
    integration_path = create_integration_file()
    
    print(f"\\n Next steps:")
    print(f"1. Install required packages: pip install nba_api aiohttp")
    print(f"2. Run integration test: python {integration_path}")
    print(f"3. Check results in C:/EQ12/logs/nba_data_sources_test.json")
    print(f"4. Integrate successful sources into your production collector")