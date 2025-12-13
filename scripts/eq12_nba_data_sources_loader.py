#!/usr/bin/env python3
"""
EQ12 NBA Data Sources Loader
Validates and loads the NBA data sources config for cluster integration
"""

import json
import sys
from pathlib import Path

def load_nba_data_sources():
    """Load and validate NBA data sources configuration"""
    config_path = Path("C:/EQ12/configs/nba_data_sources.json")
    
    if not config_path.exists():
        print(f" Config file not found: {config_path}")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        sources = config.get('data_sources', [])
        metadata = config.get('metadata', {})
        
        print(f" Loaded {len(sources)} NBA data sources")
        print(f" Categories: {metadata.get('categories', {})}")
        print(f" Auth Required: {metadata.get('auth_distribution', {})}")
        
        # Filter by integration level
        core_sources = [s for s in sources if s.get('integration_level') == 'core']
        optional_sources = [s for s in sources if s.get('integration_level') == 'optional']
        advanced_sources = [s for s in sources if s.get('integration_level') == 'advanced']
        
        print(f"\n Integration Priority:")
        print(f"   Core: {len(core_sources)} sources")
        print(f"   Optional: {len(optional_sources)} sources")
        print(f"   Advanced: {len(advanced_sources)} sources")
        
        # Show first 5 core sources for quick start
        print(f"\n Top 5 Core Sources for EQ12:")
        for i, source in enumerate(core_sources[:5], 1):
            auth_status = "" if source.get('auth_required') else ""
            print(f"   {i}. {source['name']} ({source['type']}) {auth_status}")
            print(f"      Coverage: {source.get('coverage', 'N/A')}")
            print(f"      URL: {source['url']}")
        
        return config
        
    except json.JSONDecodeError as e:
        print(f" JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f" Error loading config: {e}")
        return None

def get_sources_by_type(config, source_type):
    """Get sources filtered by type (api, repo, dataset, container)"""
    if not config:
        return []
    
    sources = config.get('data_sources', [])
    return [s for s in sources if s.get('type') == source_type]

def get_sources_by_integration_level(config, level):
    """Get sources filtered by integration level (core, optional, advanced)"""
    if not config:
        return []
    
    sources = config.get('data_sources', [])
    return [s for s in sources if s.get('integration_level') == level]

if __name__ == "__main__":
    print(" EQ12 NBA Data Sources Loader")
    print("=" * 50)
    
    config = load_nba_data_sources()
    
    if config:
        print(f"\n Configuration loaded successfully!")
        print(f" Ready for integration into your EQ12 cluster")
        
        # Show API sources for immediate use
        api_sources = get_sources_by_type(config, 'api')
        free_apis = [s for s in api_sources if not s.get('auth_required')]
        
        print(f"\n Free APIs ready for immediate use:")
        for api in free_apis[:3]:
            print(f"    {api['name']}: {api['url']}")
    else:
        print(" Failed to load configuration")
        sys.exit(1)