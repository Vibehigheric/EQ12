#!/usr/bin/env python3
"""
EQ12 Telegram Parlay Alert Test - Simple Version
Test the complete workflow without Unicode console issues
"""

import asyncio
import os
import sys

# Add scripts directory for Telegram alerts
scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from eq12_telegram_alerts import ParlayAlertManager


async def test_complete_workflow():
    """Test the complete parlay alert workflow"""

    print("=" * 60)
    print("EQ12 TELEGRAM PARLAY ALERT WORKFLOW TEST")
    print("=" * 60)

    try:
        # Initialize alert manager
        print("1. Initializing alert manager...")
        alert_manager = ParlayAlertManager()
        print("   SUCCESS: Alert manager initialized")

        # Test 1: High ROI parlay (should send)
        print("\n2. Testing HIGH ROI parlay (12.3x)...")
        high_roi_parlay = [
            {
                "team": "Denver Broncos",
                "bet_type": "+4.5",
                "odds": 110,
                "decimal_odds": 2.10,
                "line": "+4.5",
            },
            {
                "team": "Game Total",
                "bet_type": "Over 47.5",
                "odds": -105,
                "decimal_odds": 1.95,
                "line": "47.5",
            },
            {
                "team": "Golden State Warriors",
                "bet_type": "-2.5",
                "odds": -110,
                "decimal_odds": 1.91,
                "line": "-2.5",
            },
        ]

        alert = alert_manager.create_parlay_alert(
            parlay_legs=high_roi_parlay, stake_amount=8.0, min_roi_multiplier=10.0
        )

        if alert:
            print(f"   CREATED: Alert with {alert.roi_multiplier:.1f}x ROI")
            success = await alert_manager.send_alert(alert)
            if success:
                print("   SUCCESS: High ROI alert sent to Telegram!")
            else:
                print("   FAILED: Could not send high ROI alert")
                return False
        else:
            print("   FAILED: Could not create high ROI alert")
            return False

        # Test 2: Low ROI parlay (should NOT send)
        print("\n3. Testing LOW ROI parlay (5x - below threshold)...")
        low_roi_parlay = [
            {
                "team": "Team A",
                "bet_type": "+3.5",
                "odds": 150,
                "decimal_odds": 2.50,
                "line": "+3.5",
            },
            {
                "team": "Team B",
                "bet_type": "Under 40",
                "odds": 120,
                "decimal_odds": 2.20,
                "line": "40",
            },
        ]

        alert = alert_manager.create_parlay_alert(
            parlay_legs=low_roi_parlay,
            stake_amount=8.0,
            min_roi_multiplier=10.0,  # This should reject the 5x ROI parlay
        )

        if alert:
            print("   ERROR: Low ROI alert should not have been created!")
            return False
        else:
            print("   SUCCESS: Low ROI parlay correctly rejected")

        # Test 3: Status notification
        print("\n4. Testing system status notification...")
        success = await alert_manager.alerter.send_system_status("health")
        if success:
            print("   SUCCESS: Health status sent to Telegram!")
        else:
            print("   FAILED: Could not send status notification")
            return False

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! Telegram parlay alerts are working perfectly!")
        print("=" * 60)
        print("\nSummary:")
        print("- High ROI parlays (10x+) are being detected and sent")
        print("- Low ROI parlays are being filtered out correctly")
        print("- System status notifications are working")
        print("- Ready for live parlay monitoring!")

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        return False


async def send_startup_notification():
    """Send notification that the system is ready"""
    try:
        alert_manager = ParlayAlertManager()
        message = """🚀 EQ12 LIVE PARLAY SYSTEM ACTIVATED!

✅ Telegram alerts: ONLINE
✅ Math engine: READY
✅ Parlay scanner: MONITORING

🎯 Target: $8 → $80 (10x ROI)
📊 Scanning for optimal opportunities...

System will send alerts when parlays with 10x+ ROI are found!"""

        success = await alert_manager.alerter._send_telegram_message(message)
        if success:
            print("SUCCESS: Startup notification sent!")
        else:
            print("FAILED: Could not send startup notification")

    except Exception as e:
        print(f"ERROR sending startup notification: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--startup", action="store_true", help="Send startup notification")
    args = parser.parse_args()

    if args.startup:
        asyncio.run(send_startup_notification())
    else:
        success = asyncio.run(test_complete_workflow())
        sys.exit(0 if success else 1)
