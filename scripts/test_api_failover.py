#!/usr/bin/env python3
"""
EQ12 NBA API Failover Test
Test the intelligent API failover and cycling system
"""

import asyncio
import aiohttp
import sys
import json
from datetime import datetime
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from eq12_nba_production_collector import NBAProductionCollector

async def test_api_failover():
    """Test the API failover system with detailed logging"""
    print(" EQ12 NBA API Failover Test")
    print("=" * 50)
    
    # Initialize collector
    collector = NBAProductionCollector()
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health Check
        print("\n Testing API Health Check...")
        health_status = await collector.check_api_health(session)
        
        for api_name, health in health_status.items():
            status_emoji = {"healthy": "", "degraded": "", "failed": ""}.get(health.get("status"), "")
            response_time = health.get("response_time", 0)
            error = health.get("error")
            
            print(f"  {status_emoji} {api_name}: {health.get('status')} ({response_time:.2f}s)")
            if error:
                print(f"       Error: {error}")
        
        # Test 2: Priority Order
        print("\n Testing API Priority Order...")
        priority_apis = collector.get_api_priority_order(health_status)
        
        for i, (name, func, args) in enumerate(priority_apis, 1):
            health = health_status.get(name, {})
            status = health.get("status", "unknown")
            response_time = health.get("response_time", 0)
            print(f"  {i}. {name} - {status} ({response_time:.2f}s)")
        
        # Test 3: Failover Collection
        print("\n Testing Intelligent Failover Collection...")
        results = await collector.collect_all_free_sources(session)
        
        print("\n Final Results:")
        total_records = 0
        for source, data in results.items():
            count = len(data)
            total_records += count
            status_emoji = "" if count > 0 else ""
            print(f"  {status_emoji} {source}: {count} records")
        
        print(f"\n Total Records Collected: {total_records}")
        
        # Test 4: Detailed Source Analysis
        print("\n Detailed Source Analysis:")
        for source, data in results.items():
            if data:
                sample = data[0]
                print(f"   {source} Sample Data:")
                print(f"     Game: {sample.get('home_team', 'N/A')} vs {sample.get('away_team', 'N/A')}")
                print(f"     Status: {sample.get('status', 'N/A')}")
                print(f"     Collection Time: {sample.get('collection_time', 'N/A')}")
        
        # Test 5: Performance Metrics
        print("\n Performance Analysis:")
        working_apis = [source for source, data in results.items() if data]
        failed_apis = [source for source, data in results.items() if not data]
        
        success_rate = (len(working_apis) / len(results)) * 100
        print(f"  Success Rate: {success_rate:.1f}% ({len(working_apis)}/{len(results)} APIs)")
        print(f"  Working APIs: {', '.join(working_apis) if working_apis else 'None'}")
        print(f"  Failed APIs: {', '.join(failed_apis) if failed_apis else 'None'}")
        
        # Test 6: Recommendations
        print("\n System Recommendations:")
        if success_rate >= 67:  # At least 2/3 APIs working
            print("   System is operating optimally")
        elif success_rate >= 33:  # At least 1/3 APIs working
            print("   System is degraded but functional")
            print("   Consider checking failed API configurations")
        else:
            print("   System requires immediate attention")
            print("   Multiple API failures detected")
        
        return {
            "health_status": health_status,
            "results": results,
            "success_rate": success_rate,
            "total_records": total_records
        }

if __name__ == "__main__":
    try:
        test_results = asyncio.run(test_api_failover())
        
        # Save test results
        test_file = Path("C:/EQ12/logs") / f"api_failover_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(test_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        print(f"\n Test results saved: {test_file}")
        print("\n API Failover Test Complete!")
        
    except Exception as e:
        print(f"\n Test failed: {e}")
        sys.exit(1)