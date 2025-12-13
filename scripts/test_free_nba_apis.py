#!/usr/bin/env python3
"""
Quick test of enhanced NBA collection with free APIs
"""

import asyncio
import json
from datetime import datetime

try:
    import aiohttp
    print(" aiohttp imported successfully")
except ImportError:
    print(" aiohttp not available")

try:
    from nba_api.stats.endpoints import scoreboardv2
    print(" nba_api imported successfully")
    NBA_API_AVAILABLE = True
except ImportError:
    print(" nba_api not available")
    NBA_API_AVAILABLE = False

async def test_free_apis():
    """Test the free NBA APIs"""
    print("\n Testing Free NBA APIs...")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Test NBA API
    if NBA_API_AVAILABLE:
        try:
            print(" Testing NBA API...")
            scoreboard = scoreboardv2.ScoreboardV2()
            games_data = scoreboard.get_data_frames()[0]
            
            results['tests']['nba_api'] = {
                'status': 'SUCCESS',
                'records': len(games_data),
                'sample': games_data.head(3).to_dict('records') if not games_data.empty else []
            }
            print(f"    NBA API: {len(games_data)} games found")
        except Exception as e:
            results['tests']['nba_api'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"    NBA API error: {e}")
    
    # Test Ball Don't Lie API
    try:
        print(" Testing Ball Don't Lie API...")
        async with aiohttp.ClientSession() as session:
            url = "https://www.balldontlie.io/api/v1/games"
            params = {'seasons[]': 2024, 'per_page': 5}
            
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    games = data.get('data', [])
                    
                    results['tests']['balldontlie'] = {
                        'status': 'SUCCESS',
                        'records': len(games),
                        'sample': games[:2]
                    }
                    print(f"    Ball Don't Lie: {len(games)} games found")
                else:
                    results['tests']['balldontlie'] = {
                        'status': 'ERROR',
                        'error': f"HTTP {response.status}"
                    }
                    print(f"    Ball Don't Lie error: HTTP {response.status}")
    except Exception as e:
        results['tests']['balldontlie'] = {
            'status': 'ERROR',
            'error': str(e)
        }
        print(f"    Ball Don't Lie error: {e}")
    
    # Test ESPN API
    try:
        print(" Testing ESPN API...")
        async with aiohttp.ClientSession() as session:
            url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
            
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    events = data.get('events', [])
                    
                    results['tests']['espn'] = {
                        'status': 'SUCCESS',
                        'records': len(events),
                        'sample': events[:2] if events else []
                    }
                    print(f"    ESPN: {len(events)} games found")
                else:
                    results['tests']['espn'] = {
                        'status': 'ERROR',
                        'error': f"HTTP {response.status}"
                    }
                    print(f"    ESPN error: HTTP {response.status}")
    except Exception as e:
        results['tests']['espn'] = {
            'status': 'ERROR',
            'error': str(e)
        }
        print(f"    ESPN error: {e}")
    
    # Save results
    test_file = "C:/EQ12/logs/free_apis_test_results.json"
    with open(test_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n Test results saved: {test_file}")
    
    # Summary
    successful_tests = sum(1 for test in results['tests'].values() if test['status'] == 'SUCCESS')
    total_tests = len(results['tests'])
    
    print(f"\n Summary: {successful_tests}/{total_tests} APIs working")
    
    return results

if __name__ == "__main__":
    print(" EQ12 Free NBA APIs Test")
    print("=" * 40)
    
    results = asyncio.run(test_free_apis())
    
    if all(test['status'] == 'SUCCESS' for test in results['tests'].values()):
        print("\n ALL FREE APIs WORKING!")
    else:
        print("\n Some APIs need attention")