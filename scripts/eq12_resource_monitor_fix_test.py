#!/usr/bin/env python3
"""
EQ12 Resource Monitor Fix Verification
Quick test to verify the monitoring loop works without errors.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the parent directory to the path to import the monitor
sys.path.append(str(Path(__file__).parent.parent))

from eq12_resource_monitor_wrapper import EQ12ResourceMonitorWrapper

async def test_monitoring_cycle():
    """Test a single monitoring cycle to verify all methods work."""
    print(" Testing EQ12 Resource Monitor Fix...")
    
    # Setup minimal logging
    logging.basicConfig(level=logging.INFO)
    
    # Create monitor instance
    monitor = EQ12ResourceMonitorWrapper("C:\\EQ12")
    
    try:
        print(" Step 1: Initializing monitor...")
        
        print(" Step 2: Collecting metrics...")
        monitoring_data = await monitor._collect_comprehensive_metrics()
        
        print(" Step 3: Processing monitoring data...")
        await monitor._process_monitoring_data(monitoring_data)
        
        print(" Step 4: Checking alert conditions...")
        await monitor._check_alert_conditions(monitoring_data)
        
        print(" Step 5: Saving metrics to database...")
        await monitor._save_metrics_to_db(monitoring_data)
        
        print("\n SUCCESS: All monitoring methods work correctly!")
        print(f" Health Score: {monitoring_data['overall_health_score']:.1f}%")
        print(f" Alerts: {len(monitoring_data.get('alerts', []))}")
        print(f"  CPU: {monitoring_data['system']['cpu_percent']:.1f}%")
        print(f" Memory: {monitoring_data['system']['memory']['percent']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f" ERROR: {e}")
        return False

async def main():
    """Main test function."""
    success = await test_monitoring_cycle()
    if success:
        print("\n Resource monitor is now working correctly!")
        print("The '_process_monitoring_data' method has been successfully implemented.")
    else:
        print("\n There are still issues with the resource monitor.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)