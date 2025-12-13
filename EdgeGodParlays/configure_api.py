#!/usr/bin/env python3
"""
EdgeGod API Configuration and Usage Optimizer
Helps configure optimal API usage patterns and monitor quota consumption
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from api_manager import EdgeGodAPIManager


class EdgeGodAPIOptimizer:
    """Optimize API usage patterns for The Odds API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_manager = EdgeGodAPIManager(api_key)

        # Usage patterns
        self.optimal_schedules = {
            "conservative": {
                "calls_per_hour": 15,
                "daily_limit": 360,
                "cache_duration": 1800,  # 30 minutes
                "batch_size": 10,
            },
            "moderate": {
                "calls_per_hour": 25,
                "daily_limit": 400,
                "cache_duration": 900,  # 15 minutes
                "batch_size": 20,
            },
            "aggressive": {
                "calls_per_hour": 40,
                "daily_limit": 450,
                "cache_duration": 300,  # 5 minutes
                "batch_size": 30,
            },
        }

    async def analyze_current_usage(self) -> dict:
        """Analyze current API usage and provide recommendations"""
        try:
            health = await self.api_manager.health_check()
            stats = self.api_manager.get_usage_stats()

            # Calculate efficiency metrics
            cache_hit_rate = stats["cache"]["hit_rate"]
            success_rate = stats["requests"]["success_rate"]
            quota_efficiency = (
                (stats["quota"]["daily_used"] / stats["quota"]["daily_limit"]) * 100
                if stats["quota"]["daily_limit"] > 0
                else 0
            )

            recommendations = []

            # Cache recommendations
            if cache_hit_rate < 30:
                recommendations.append(
                    {
                        "type": "cache",
                        "priority": "high",
                        "message": f"Low cache hit rate ({cache_hit_rate:.1f}%). Increase cache duration or reduce unnecessary calls.",
                    }
                )

            # Success rate recommendations
            if success_rate < 95:
                recommendations.append(
                    {
                        "type": "reliability",
                        "priority": "high",
                        "message": f"Low success rate ({success_rate:.1f}%). Check for rate limiting or quota issues.",
                    }
                )

            # Quota recommendations
            if quota_efficiency > 80:
                recommendations.append(
                    {
                        "type": "quota",
                        "priority": "medium",
                        "message": f"High quota usage ({quota_efficiency:.1f}%). Consider upgrading plan or optimizing calls.",
                    }
                )

            return {
                "status": health.get("status", "unknown"),
                "current_usage": stats,
                "efficiency_metrics": {
                    "cache_hit_rate": cache_hit_rate,
                    "success_rate": success_rate,
                    "quota_efficiency": quota_efficiency,
                },
                "recommendations": recommendations,
                "optimal_schedule": self._recommend_schedule(stats),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "recommendations": [
                    {
                        "type": "error",
                        "priority": "critical",
                        "message": f"Failed to analyze usage: {e}",
                    }
                ],
            }

    def _recommend_schedule(self, stats: dict) -> str:
        """Recommend optimal usage schedule based on current patterns"""
        daily_used = stats["quota"]["daily_used"]

        if daily_used < 100:
            return "conservative"
        if daily_used < 300:
            return "moderate"
        return "aggressive"

    async def test_api_endpoints(self) -> dict:
        """Test various API endpoints to ensure they're working correctly"""
        results = {}

        # Test sports endpoint
        try:
            sports = await self.api_manager.get_sports()
            results["sports"] = {
                "status": "success",
                "count": len(sports),
                "sample": sports[:3] if sports else [],
            }
        except Exception as e:
            results["sports"] = {"status": "error", "error": str(e)}

        # Test events endpoint (MLB)
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            events = await self.api_manager.get_events(
                "baseball_mlb", f"{today}T00:00:00Z", f"{today}T23:59:59Z"
            )
            results["events"] = {
                "status": "success",
                "count": len(events),
                "sample": events[:2] if events else [],
            }

            # Test odds endpoint if we have events
            if events:
                event_ids = [events[0]["id"]] if events else []
                odds = await self.api_manager.get_odds("baseball_mlb", event_ids=event_ids)
                results["odds"] = {
                    "status": "success",
                    "count": len(odds),
                    "markets_available": (
                        list(
                            set(
                                [
                                    market["key"]
                                    for odds_event in odds
                                    for bookmaker in odds_event.get("bookmakers", [])
                                    for market in bookmaker.get("markets", [])
                                ]
                            )
                        )
                        if odds
                        else []
                    ),
                }
        except Exception as e:
            results["events"] = {"status": "error", "error": str(e)}
            results["odds"] = {"status": "skipped", "reason": "Events endpoint failed"}

        return results

    def generate_usage_schedule(self, schedule_type: str = "moderate") -> dict:
        """Generate optimal usage schedule"""
        if schedule_type not in self.optimal_schedules:
            schedule_type = "moderate"

        schedule = self.optimal_schedules[schedule_type].copy()

        # Calculate timing recommendations
        calls_per_hour = schedule["calls_per_hour"]
        minutes_between_calls = 60 / calls_per_hour

        schedule["timing"] = {
            "calls_per_hour": calls_per_hour,
            "minutes_between_calls": round(minutes_between_calls, 1),
            "recommended_intervals": [
                f"{i * minutes_between_calls:.0f}min" for i in range(1, min(6, calls_per_hour + 1))
            ],
        }

        # Add market recommendations
        schedule["recommended_markets"] = {
            "essential": ["h2h", "spreads", "totals"],
            "mlb_props": ["player_home_runs", "player_total_bases"],
            "advanced": ["player_hits", "player_runs", "team_total"],
        }

        return schedule

    async def monitor_quota_usage(self, duration_hours: int = 24) -> dict:
        """Monitor API quota usage over time"""
        monitoring_data = {
            "start_time": datetime.now().isoformat(),
            "duration_hours": duration_hours,
            "samples": [],
        }

        print(f"Starting {duration_hours}-hour quota monitoring...")

        try:
            for hour in range(duration_hours):
                sample_time = datetime.now()
                stats = self.api_manager.get_usage_stats()

                sample = {
                    "hour": hour,
                    "timestamp": sample_time.isoformat(),
                    "quota_used": stats["quota"]["daily_used"],
                    "requests_made": stats["requests"]["total"],
                    "cache_hits": stats["requests"]["cached"],
                    "errors": stats["requests"]["failed"],
                }

                monitoring_data["samples"].append(sample)

                print(
                    f"Hour {hour + 1}: Quota {stats['quota']['daily_used']}/{stats['quota']['daily_limit']}, "
                    f"Requests: {stats['requests']['total']}, Cache hits: {stats['requests']['cached']}"
                )

                # Wait 1 hour (or shorter for testing)
                if hour < duration_hours - 1:
                    await asyncio.sleep(3600)  # 1 hour

            return monitoring_data

        except KeyboardInterrupt:
            print("Monitoring interrupted by user")
            return monitoring_data
        except Exception as e:
            print(f"Monitoring error: {e}")
            return monitoring_data


async def main():
    """Main configuration and optimization utility"""
    api_key = os.environ.get("ODDS_API_KEY", "")
    if not api_key:
        print("❌ Please set ODDS_API_KEY environment variable")
        return

    print("🎯 EdgeGod API Configuration & Optimization Utility")
    print("=" * 60)

    optimizer = EdgeGodAPIOptimizer(api_key)

    try:
        # Analyze current usage
        print("📊 Analyzing current API usage patterns...")
        analysis = await optimizer.analyze_current_usage()

        print(f"\n🔍 API Status: {analysis['status'].upper()}")

        if "efficiency_metrics" in analysis:
            metrics = analysis["efficiency_metrics"]
            print(f"📈 Cache Hit Rate: {metrics['cache_hit_rate']:.1f}%")
            print(f"✅ Success Rate: {metrics['success_rate']:.1f}%")
            print(f"📊 Quota Usage: {metrics['quota_efficiency']:.1f}%")

        # Show recommendations
        if analysis.get("recommendations"):
            print("\n💡 Recommendations:")
            for rec in analysis["recommendations"]:
                priority_icon = {"critical": "🚨", "high": "⚠️", "medium": "ℹ️"}.get(
                    rec["priority"], "💡"
                )
                print(f"  {priority_icon} {rec['message']}")

        # Test API endpoints
        print("\n🧪 Testing API endpoints...")
        test_results = await optimizer.test_api_endpoints()

        for endpoint, result in test_results.items():
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"  {status_icon} {endpoint.title()}: {result.get('count', 'N/A')} items")

        # Generate optimal schedule
        schedule_type = analysis.get("optimal_schedule", "moderate")
        print(f"\n📅 Generating optimal schedule ({schedule_type})...")
        schedule = optimizer.generate_usage_schedule(schedule_type)

        print(f"  📞 Calls per hour: {schedule['timing']['calls_per_hour']}")
        print(f"  ⏰ Minutes between calls: {schedule['timing']['minutes_between_calls']}")
        print(f"  📦 Batch size: {schedule['batch_size']}")
        print(f"  💾 Cache duration: {schedule['cache_duration']/60:.0f} minutes")

        # Save configuration
        logs_dir = Path(os.environ.get("EQ12_LOGS", "./logs"))
        logs_dir.mkdir(exist_ok=True)

        config_file = logs_dir / "edgegod_api_config.json"
        config_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "test_results": test_results,
            "recommended_schedule": schedule,
            "environment_config": {
                "ODDS_API_KEY": "SET" if api_key else "MISSING",
                "EQ12_LOGS": str(logs_dir),
            },
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)

        print(f"\n💾 Configuration saved to: {config_file}")

        # Offer monitoring
        monitor = input("\n🔍 Would you like to start quota monitoring? (y/N): ").lower().strip()
        if monitor == "y":
            hours = input("How many hours to monitor? (default: 1): ").strip()
            try:
                hours = int(hours) if hours else 1
                monitoring_data = await optimizer.monitor_quota_usage(hours)

                monitor_file = (
                    logs_dir / f'quota_monitoring_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                )
                with open(monitor_file, "w") as f:
                    json.dump(monitoring_data, f, indent=2)

                print(f"📊 Monitoring data saved to: {monitor_file}")
            except ValueError:
                print("Invalid number of hours")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        await optimizer.api_manager.close()

    print("\n🎯 EdgeGod API optimization complete!")


if __name__ == "__main__":
    asyncio.run(main())
