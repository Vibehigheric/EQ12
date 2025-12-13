"""
EQ12 Health Monitor Service
Monitors system health and service availability
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import aiohttp


class HealthMonitor:
    """System health monitoring service"""

    def __init__(self):
        self.setup_logging()
        self.health_file = Path("logs/health/status.json")
        self.endpoints = {
            "dashboard": "http://localhost:3000/health",
            "ngrok": "http://127.0.0.1:4040/api/tunnels",
        }

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs/health")
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / f"health_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler(),
            ],
        )

    async def check_endpoint_health(self, name: str, url: str) -> dict:
        """Check health of a single endpoint"""
        start_time = datetime.now()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    response_time = (datetime.now() - start_time).total_seconds()

                    return {
                        "name": name,
                        "url": url,
                        "status": "healthy",
                        "http_status": response.status,
                        "response_time_ms": round(response_time * 1000, 2),
                        "timestamp": start_time.isoformat(),
                    }

        except TimeoutError:
            return {
                "name": name,
                "url": url,
                "status": "timeout",
                "error": "Request timeout after 5 seconds",
                "timestamp": start_time.isoformat(),
            }
        except Exception as e:
            return {
                "name": name,
                "url": url,
                "status": "error",
                "error": str(e),
                "timestamp": start_time.isoformat(),
            }

    async def check_all_health(self) -> dict:
        """Check health of all monitored services"""
        logging.info("Starting health check cycle")

        # Check all endpoints
        tasks = [self.check_endpoint_health(name, url) for name, url in self.endpoints.items()]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "services": {},
            "summary": {
                "total_services": len(self.endpoints),
                "healthy_services": 0,
                "unhealthy_services": 0,
                "avg_response_time_ms": 0,
            },
        }

        total_response_time = 0
        response_count = 0

        for result in results:
            if isinstance(result, dict):
                service_name = result["name"]
                health_data["services"][service_name] = result

                if result["status"] == "healthy":
                    health_data["summary"]["healthy_services"] += 1
                    if "response_time_ms" in result:
                        total_response_time += result["response_time_ms"]
                        response_count += 1
                else:
                    health_data["summary"]["unhealthy_services"] += 1
                    health_data["overall_status"] = "degraded"

        # Calculate average response time
        if response_count > 0:
            avg_time = total_response_time / response_count
            health_data["summary"]["avg_response_time_ms"] = round(avg_time, 2)

        # Determine overall status
        if health_data["summary"]["unhealthy_services"] == 0:
            health_data["overall_status"] = "healthy"
        elif health_data["summary"]["healthy_services"] > 0:
            health_data["overall_status"] = "degraded"
        else:
            health_data["overall_status"] = "critical"

        # Save health data
        self.save_health_data(health_data)

        logging.info(
            f"Health check complete: {health_data['overall_status']} "
            f"({health_data['summary']['healthy_services']}/{health_data['summary']['total_services']} healthy)"
        )

        return health_data

    def save_health_data(self, health_data: dict):
        """Save health data to file"""
        try:
            self.health_file.parent.mkdir(parents=True, exist_ok=True)
            self.health_file.write_text(json.dumps(health_data, indent=2))
        except Exception as e:
            logging.error(f"Failed to save health data: {e}")

    def get_current_health(self) -> dict:
        """Get current health status from file"""
        try:
            if self.health_file.exists():
                return json.loads(self.health_file.read_text())
        except Exception as e:
            logging.error(f"Failed to read health data: {e}")

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "error": "No health data available",
        }

    async def monitor_continuously(self, interval_seconds: int = 60):
        """Run health monitoring continuously"""
        logging.info(f"Starting continuous health monitoring (interval: {interval_seconds}s)")

        while True:
            try:
                health_data = await self.check_all_health()

                # Alert on critical status
                if health_data["overall_status"] == "critical":
                    logging.error("CRITICAL: All services are down!")
                elif health_data["overall_status"] == "degraded":
                    unhealthy = health_data["summary"]["unhealthy_services"]
                    logging.warning(f"DEGRADED: {unhealthy} service(s) down")

                await asyncio.sleep(interval_seconds)

            except KeyboardInterrupt:
                logging.info("Stopping health monitor")
                break
            except Exception as e:
                logging.error(f"Health monitor error: {e}")
                await asyncio.sleep(30)  # Wait before retry


async def main():
    """Main entry point"""
    monitor = HealthMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "check":
            # Single health check
            health_data = await monitor.check_all_health()
            print(json.dumps(health_data, indent=2))

        elif command == "status":
            # Get current status
            current_health = monitor.get_current_health()
            print(json.dumps(current_health, indent=2))

        elif command == "monitor":
            # Continuous monitoring
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            await monitor.monitor_continuously(interval)

        else:
            print(f"Unknown command: {command}")
            print("Usage: python health_monitor.py [check|status|monitor] [interval]")
            return 1
    else:
        # Default: single check
        health_data = await monitor.check_all_health()
        print(json.dumps(health_data, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
