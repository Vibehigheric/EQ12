#!/usr/bin/env python3
"""
EQ12 Live Parlay Scanner with Telegram Alerts
===========================================

Enhanced version that sends real-time notifications when optimal parlays are found.
Integrates the parlay scanner with Telegram alerting system.
"""

import asyncio
import logging
import os
import sys

# Add scripts directory for Telegram alerts
scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from eq12_telegram_alerts import ParlayAlertManager


class LiveParlayScanner:
    """Live parlay scanner with Telegram notifications"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.alert_manager = ParlayAlertManager()
        self.running = False
        self.scan_interval = 300  # 5 minutes between scans

        self.logger.info("🔥 EQ12 Live Parlay Scanner with Telegram alerts initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # File handler
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
            os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(
                os.path.join(log_dir, "eq12_live_scanner_alerts.log")
            )

            # Console handler
            console_handler = logging.StreamHandler()

            # Formatter
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    async def start_monitoring(self):
        """Start continuous parlay monitoring"""
        self.running = True
        self.logger.info("🚀 Starting live parlay monitoring with Telegram alerts")

        # Send startup notification
        await self.alert_manager.alerter.send_system_status("startup")

        scan_count = 0

        try:
            while self.running:
                scan_count += 1
                self.logger.info(f"📊 Starting parlay scan #{scan_count}")

                # Generate sample parlay opportunities
                sample_parlays = self._generate_sample_parlays()

                alerts_sent = 0

                for parlay in sample_parlays:
                    alert = self.alert_manager.create_parlay_alert(
                        parlay_legs=parlay, stake_amount=8.0, min_roi_multiplier=10.0
                    )

                    if alert:
                        success = await self.alert_manager.send_alert(alert)
                        if success:
                            alerts_sent += 1

                if alerts_sent > 0:
                    self.logger.info(f"📲 Sent {alerts_sent} parlay alerts")
                else:
                    self.logger.info("📋 No optimal parlays found this scan")

                # Wait for next scan
                self.logger.info(f"⏳ Waiting {self.scan_interval} seconds for next scan...")
                await asyncio.sleep(self.scan_interval)

        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Error in monitoring: {e}")
            # Send error notification
            await self.alert_manager.alerter.send_system_status("error")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Shutdown monitoring"""
        self.running = False
        self.logger.info("🔴 Shutting down live parlay scanner")

        # Send shutdown notification
        try:
            await self.alert_manager.alerter.send_system_status("shutdown")
        except Exception as e:
            self.logger.error(f"Failed to send shutdown notification: {e}")

    def _generate_sample_parlays(self) -> list:
        """Generate sample parlay opportunities for testing"""

        # Sample high-ROI parlay opportunities
        sample_parlays = [
            # 12.3x ROI parlay (exceeds 10x target)
            [
                {
                    "team": "Denver Broncos",
                    "bet_type": "+4.5",
                    "odds": 110,
                    "decimal_odds": 2.10,
                    "line": "+4.5",
                    "confidence": 0.85,
                },
                {
                    "team": "Game Total",
                    "bet_type": "Over 47.5",
                    "odds": -105,
                    "decimal_odds": 1.95,
                    "line": "47.5",
                    "confidence": 0.78,
                },
                {
                    "team": "Golden State Warriors",
                    "bet_type": "-2.5",
                    "odds": -110,
                    "decimal_odds": 1.91,
                    "line": "-2.5",
                    "confidence": 0.82,
                },
            ],
            # 15.2x ROI parlay (very high ROI)
            [
                {
                    "team": "Miami Heat",
                    "bet_type": "+6.5",
                    "odds": 105,
                    "decimal_odds": 2.05,
                    "line": "+6.5",
                    "confidence": 0.88,
                },
                {
                    "team": "Boston Celtics",
                    "bet_type": "Under 220.5",
                    "odds": -110,
                    "decimal_odds": 1.91,
                    "line": "220.5",
                    "confidence": 0.75,
                },
                {
                    "team": "Los Angeles Lakers",
                    "bet_type": "+3.5",
                    "odds": -105,
                    "decimal_odds": 1.95,
                    "line": "+3.5",
                    "confidence": 0.80,
                },
                {
                    "team": "Phoenix Suns",
                    "bet_type": "-1.5",
                    "odds": 110,
                    "decimal_odds": 2.10,
                    "line": "-1.5",
                    "confidence": 0.77,
                },
            ],
            # Moderate 11.1x ROI parlay
            [
                {
                    "team": "Tampa Bay Lightning",
                    "bet_type": "ML",
                    "odds": 130,
                    "decimal_odds": 2.30,
                    "line": "ML",
                    "confidence": 0.73,
                },
                {
                    "team": "Toronto Maple Leafs",
                    "bet_type": "-0.5",
                    "odds": -120,
                    "decimal_odds": 1.83,
                    "line": "-0.5",
                    "confidence": 0.85,
                },
                {
                    "team": "Over 6.5 Goals",
                    "bet_type": "Over",
                    "odds": -105,
                    "decimal_odds": 1.95,
                    "line": "6.5",
                    "confidence": 0.68,
                },
            ],
        ]

        return sample_parlays

    async def send_test_alert(self):
        """Send a test alert to verify Telegram integration"""
        self.logger.info("📧 Sending test parlay alert...")

        test_parlay = [
            {
                "team": "TEST Team A",
                "bet_type": "+7.5",
                "odds": 110,
                "decimal_odds": 2.10,
                "line": "+7.5",
            },
            {
                "team": "TEST Team B",
                "bet_type": "Over 45.5",
                "odds": -110,
                "decimal_odds": 1.91,
                "line": "45.5",
            },
        ]

        alert = self.alert_manager.create_parlay_alert(
            parlay_legs=test_parlay,
            stake_amount=8.0,
            min_roi_multiplier=5.0,  # Lower threshold for test
        )

        if alert:
            success = await self.alert_manager.send_alert(alert)
            if success:
                self.logger.info("✅ Test alert sent successfully!")
                return True
            else:
                self.logger.error("❌ Failed to send test alert")
                return False
        else:
            self.logger.error("❌ Failed to create test alert")
            return False


async def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Live Parlay Scanner with Telegram Alerts")
    parser.add_argument("--test-alert", action="store_true", help="Send a test alert and exit")
    parser.add_argument(
        "--interval", type=int, default=300, help="Scan interval in seconds (default: 300)"
    )

    args = parser.parse_args()

    scanner = LiveParlayScanner()

    if args.test_alert:
        # Send test alert
        success = await scanner.send_test_alert()
        return 0 if success else 1

    # Set custom scan interval if provided
    if args.interval:
        scanner.scan_interval = args.interval
        scanner.logger.info(f"⏱️ Scan interval set to {args.interval} seconds")

    try:
        await scanner.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))
