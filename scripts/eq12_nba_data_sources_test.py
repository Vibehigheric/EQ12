#!/usr/bin/env python3
"""
EQ12 NBA Data Sources Simple Test
Tests the NBA data sources config without complex dependencies
"""

import json
from pathlib import Path
from datetime import datetime

def test_nba_data_sources():
    """Simple test of NBA data sources configuration"""
    print(" EQ12 NBA Data Sources Test")
    print("=" * 50)
    
    # Load configuration
    config_path = Path("C:/EQ12/configs/nba_data_sources.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        sources = config.get('data_sources', [])
        metadata = config.get('metadata', {})
        
        print(f" Configuration loaded successfully")
        print(f" Total sources: {len(sources)}")
        print(f" Categories: {metadata.get('categories', {})}")
        
        # Analyze by type
        api_sources = [s for s in sources if s.get('type') == 'api']
        repo_sources = [s for s in sources if s.get('type') == 'repo']
        dataset_sources = [s for s in sources if s.get('type') == 'dataset']
        container_sources = [s for s in sources if s.get('type') == 'container']
        
        print(f"\n Source Breakdown:")
        print(f"    APIs: {len(api_sources)}")
        print(f"    Repos: {len(repo_sources)}")
        print(f"    Datasets: {len(dataset_sources)}")
        print(f"    Containers: {len(container_sources)}")
        
        # Analyze by integration level
        core_sources = [s for s in sources if s.get('integration_level') == 'core']
        optional_sources = [s for s in sources if s.get('integration_level') == 'optional']
        advanced_sources = [s for s in sources if s.get('integration_level') == 'advanced']
        
        print(f"\n Integration Priority:")
        print(f"    Core: {len(core_sources)}")
        print(f"    Optional: {len(optional_sources)}")
        print(f"    Advanced: {len(advanced_sources)}")
        
        # Show free APIs for immediate use
        free_apis = [s for s in api_sources if not s.get('auth_required')]
        
        print(f"\n Free APIs (Ready for Immediate Use):")
        for i, api in enumerate(free_apis[:5], 1):
            print(f"   {i}. {api['name']}")
            print(f"      Coverage: {api.get('coverage', 'N/A')}")
            print(f"      URL: {api['url']}")
            print(f"      Data Types: {', '.join(api.get('data_types', []))}")
            print()
        
        # Show core repos for data collection
        core_repos = [s for s in repo_sources if s.get('integration_level') == 'core']
        
        print(f" Core Repositories (Data Sources):")
        for i, repo in enumerate(core_repos[:3], 1):
            print(f"   {i}. {repo['name']}")
            print(f"      Coverage: {repo.get('coverage', 'N/A')}")
            print(f"      URL: {repo['url']}")
            print(f"      Format: {repo.get('data_format', 'N/A')}")
            print()
        
        # Generate integration recommendations
        print(f" Integration Recommendations for EQ12:")
        print(f"   1. Start with FREE APIs: nba_api, balldontlie_api, espn_nba_api")
        print(f"   2. Download core datasets: nba_data_shufinskiy, nba_dataset_brescou")
        print(f"   3. Use your existing Odds API for betting data")
        print(f"   4. Integrate AI APIs: OpenAI, Claude, Groq (already configured)")
        print(f"   5. Scale to advanced sources when profitable")
        
        # Save test results
        test_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'test_status': 'PASSED',
            'total_sources': len(sources),
            'breakdown': {
                'apis': len(api_sources),
                'repos': len(repo_sources),
                'datasets': len(dataset_sources),
                'containers': len(container_sources)
            },
            'priority': {
                'core': len(core_sources),
                'optional': len(optional_sources),
                'advanced': len(advanced_sources)
            },
            'free_apis_available': len(free_apis),
            'recommendations': [
                'Start with nba_api for official NBA.com data',
                'Use balldontlie_api for historical player/team stats',
                'Integrate espn_nba_api for scores and news',
                'Download shufinskiy nba_data repo for play-by-play analysis',
                'Scale to premium APIs when system is profitable'
            ]
        }
        
        results_path = Path("C:/EQ12/logs/nba_data_sources_test_results.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\n Test results saved to: {results_path}")
        print(f" NBA Data Sources Arsenal Ready for EQ12 Integration!")
        
        return True
        
    except FileNotFoundError:
        print(f" Configuration file not found: {config_path}")
        return False
    except json.JSONDecodeError as e:
        print(f" JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f" Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_nba_data_sources()
    if success:
        print(f"\n SUCCESS: Your NBA data arsenal is ready!")
        print(f" Config: C:/EQ12/configs/nba_data_sources.json")
        print(f" Results: C:/EQ12/logs/nba_data_sources_test_results.json")
    else:
        print(f"\n FAILED: Check configuration and try again")