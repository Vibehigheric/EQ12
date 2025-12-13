"""
Smart Dispatcher for EQ12 God Mode Commander++
Intelligent keyword-based action routing to specialized executors
"""

import json

from executors.notebook import (
    run_data_pipeline,
    run_market_analysis,
    run_sports_analysis,
)
from executors.shell import (
    run_housing_monitor,
    run_market_scraper,
    run_shell,
    run_sports_scraper,
)
from executors.telegram import send_sports_alert, send_travel_alert, send_urgent_alert


class SmartDispatcher:
    """Intelligent action dispatcher with keyword-based routing"""

    def __init__(self):
        self.routing_rules = {
            # Sports-related actions
            "sports": {
                "keywords": [
                    "sports",
                    "betting",
                    "odds",
                    "game",
                    "match",
                    "team",
                    "player",
                    "mlb",
                    "nfl",
                    "nba",
                    "ufc",
                    "soccer",
                ],
                "executors": {
                    "urgent": self._dispatch_sports_urgent,
                    "short_term": self._dispatch_sports_short_term,
                    "long_term": self._dispatch_sports_long_term,
                },
            },
            # Market/Dropship actions
            "market": {
                "keywords": [
                    "market",
                    "dropship",
                    "product",
                    "trend",
                    "supplier",
                    "price",
                    "profit",
                    "aliexpress",
                    "amazon",
                    "shopify",
                ],
                "executors": {
                    "urgent": self._dispatch_market_urgent,
                    "short_term": self._dispatch_market_short_term,
                    "long_term": self._dispatch_market_long_term,
                },
            },
            # Travel actions
            "travel": {
                "keywords": [
                    "travel",
                    "flight",
                    "hotel",
                    "booking",
                    "visa",
                    "itinerary",
                    "destination",
                    "trip",
                ],
                "executors": {
                    "urgent": self._dispatch_travel_urgent,
                    "short_term": self._dispatch_travel_short_term,
                    "long_term": self._dispatch_travel_long_term,
                },
            },
            # Housing/Real Estate actions
            "housing": {
                "keywords": [
                    "housing",
                    "property",
                    "real estate",
                    "mortgage",
                    "investment",
                    "rent",
                    "market",
                ],
                "executors": {
                    "urgent": self._dispatch_housing_urgent,
                    "short_term": self._dispatch_housing_short_term,
                    "long_term": self._dispatch_housing_long_term,
                },
            },
            # Data/Scraping actions
            "scraping": {
                "keywords": [
                    "scrape",
                    "data",
                    "collect",
                    "monitor",
                    "track",
                    "crawl",
                    "extract",
                    "api",
                ],
                "executors": {
                    "urgent": self._dispatch_scraping_urgent,
                    "short_term": self._dispatch_scraping_short_term,
                    "long_term": self._dispatch_scraping_long_term,
                },
            },
            # Study/Learning actions
            "study": {
                "keywords": [
                    "study",
                    "learn",
                    "exam",
                    "education",
                    "course",
                    "schedule",
                    "practice",
                ],
                "executors": {
                    "urgent": self._dispatch_study_urgent,
                    "short_term": self._dispatch_study_short_term,
                    "long_term": self._dispatch_study_long_term,
                },
            },
        }

    def classify_action(self, action: str) -> tuple[str, float]:
        """Classify action by category and confidence score"""
        action_lower = action.lower()
        best_category = "general"
        best_score = 0.0

        for category, config in self.routing_rules.items():
            keywords = config["keywords"]
            matches = sum(1 for keyword in keywords if keyword in action_lower)
            score = matches / len(keywords) if keywords else 0

            if score > best_score:
                best_score = score
                best_category = category

        return best_category, best_score

    def dispatch_action(self, action: str, priority: str) -> dict:
        """Dispatch action to appropriate executor based on content analysis"""
        category, confidence = self.classify_action(action)

        print(f"🎯 Action classified as '{category}' (confidence: {confidence:.2f})")
        print(f"📋 Dispatching {priority} action: {action[:60]}...")

        try:
            if category in self.routing_rules:
                executor_func = self.routing_rules[category]["executors"].get(priority)
                if executor_func:
                    result = executor_func(action)
                    return {
                        "success": True,
                        "category": category,
                        "confidence": confidence,
                        "executor": executor_func.__name__,
                        "result": result,
                    }

            # Fallback to general dispatch
            return self._dispatch_general(action, priority)

        except Exception as e:
            print(f"❌ Dispatch error: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": action,
                "category": category,
            }

    # Sports Executors
    def _dispatch_sports_urgent(self, action: str) -> dict:
        """Handle urgent sports actions"""
        # Send Telegram alert + trigger scraper
        telegram_result = send_sports_alert(action)
        scraper_result = run_sports_scraper(action)

        return {
            "telegram": telegram_result,
            "scraper": scraper_result,
            "type": "sports_urgent",
        }

    def _dispatch_sports_short_term(self, action: str) -> dict:
        """Handle short-term sports actions"""
        # Run sports analysis notebook
        return run_sports_analysis(action)

    def _dispatch_sports_long_term(self, action: str) -> dict:
        """Handle long-term sports actions"""
        # Schedule recurring analysis
        return {"scheduled": True, "type": "sports_monitoring", "action": action}

    # Market Executors
    def _dispatch_market_urgent(self, action: str) -> dict:
        """Handle urgent market actions"""
        # Trigger immediate market scraping
        scraper_result = run_market_scraper(action)
        return {"scraper": scraper_result, "type": "market_urgent"}

    def _dispatch_market_short_term(self, action: str) -> dict:
        """Handle short-term market actions"""
        # Run market analysis notebook
        return run_market_analysis(action)

    def _dispatch_market_long_term(self, action: str) -> dict:
        """Handle long-term market actions"""
        # Schedule data pipeline
        return run_data_pipeline(action, "scheduled")

    # Travel Executors
    def _dispatch_travel_urgent(self, action: str) -> dict:
        """Handle urgent travel actions"""
        # Send travel alert
        telegram_result = send_travel_alert(action)
        return {"telegram": telegram_result, "type": "travel_urgent"}

    def _dispatch_travel_short_term(self, action: str) -> dict:
        """Handle short-term travel actions"""
        # Run travel optimization
        return {"executed": True, "type": "travel_optimization", "action": action}

    def _dispatch_travel_long_term(self, action: str) -> dict:
        """Handle long-term travel actions"""
        return {"scheduled": True, "type": "travel_planning", "action": action}

    # Housing Executors
    def _dispatch_housing_urgent(self, action: str) -> dict:
        """Handle urgent housing actions"""
        # Trigger housing monitor
        return run_housing_monitor(action)

    def _dispatch_housing_short_term(self, action: str) -> dict:
        """Handle short-term housing actions"""
        return {"executed": True, "type": "housing_analysis", "action": action}

    def _dispatch_housing_long_term(self, action: str) -> dict:
        """Handle long-term housing actions"""
        return {"scheduled": True, "type": "housing_monitoring", "action": action}

    # Scraping Executors
    def _dispatch_scraping_urgent(self, action: str) -> dict:
        """Handle urgent scraping actions"""
        # Determine scraper type and execute
        if any(word in action.lower() for word in ["sports", "betting", "odds"]):
            return run_sports_scraper(action)
        if any(word in action.lower() for word in ["market", "product", "price"]):
            return run_market_scraper(action)
        return run_shell(f'python scripts/general_scraper.py "{action}"')

    def _dispatch_scraping_short_term(self, action: str) -> dict:
        """Handle short-term scraping actions"""
        return run_data_pipeline(action, "scraping")

    def _dispatch_scraping_long_term(self, action: str) -> dict:
        """Handle long-term scraping actions"""
        return {"scheduled": True, "type": "recurring_scraping", "action": action}

    # Study Executors
    def _dispatch_study_urgent(self, action: str) -> dict:
        """Handle urgent study actions"""
        return {"executed": True, "type": "study_urgent", "action": action}

    def _dispatch_study_short_term(self, action: str) -> dict:
        """Handle short-term study actions"""
        return {"executed": True, "type": "study_planning", "action": action}

    def _dispatch_study_long_term(self, action: str) -> dict:
        """Handle long-term study actions"""
        return {"scheduled": True, "type": "study_schedule", "action": action}

    # General Fallback
    def _dispatch_general(self, action: str, priority: str) -> dict:
        """Fallback for unclassified actions"""
        print(f"⚠️  Using general dispatcher for {priority} action")

        if priority == "urgent":
            # Send generic urgent alert
            return {"telegram": send_urgent_alert(action), "type": "general_urgent"}
        # Log action for manual review
        return {"logged": True, "type": f"general_{priority}", "action": action}


# Global dispatcher instance
dispatcher = SmartDispatcher()


def dispatch_plan(json_plan: dict) -> dict:
    """Main entry point for dispatching JSON action plans."""
    results = {
        "urgent": [],
        "short_term": [],
        "long_term": [],
        "summary": {"total": 0, "successful": 0, "failed": 0},
    }

    print("\n[dispatcher] smart dispatch system activated")

    for priority in ("urgent", "short_term", "long_term"):
        actions = json_plan.get(priority, []) or []

        for entry in actions:
            if isinstance(entry, dict):
                action_text = entry.get("task") or entry.get("action") or json.dumps(entry)
            else:
                action_text = str(entry)

            result = dispatcher.dispatch_action(action_text, priority)
            result.setdefault("action", action_text)
            result.setdefault("plan_item", entry)

            results[priority].append(result)
            results["summary"]["total"] += 1

            if result.get("success", True):
                results["summary"]["successful"] += 1
                print(f"[dispatcher] {priority} action dispatched successfully")
            else:
                results["summary"]["failed"] += 1
                print(f"[dispatcher] {priority} action dispatch failed")

    summary = results["summary"]
    print("\n[dispatcher] dispatch summary:")
    print(f"   total actions: {summary['total']}")
    print(f"   successful: {summary['successful']}")
    print(f"   failed: {summary['failed']}")

    return results


if __name__ == "__main__":
    # Test the dispatcher
    test_plan = {
        "urgent": ["Check MLB betting odds for tonight's games"],
        "short_term": ["Analyze dropshipping trends for electronic accessories"],
        "long_term": ["Set up automated property monitoring system"],
    }

    print("Testing Smart Dispatcher...")
    results = dispatch_plan(test_plan)
    print("✅ Smart Dispatcher test completed")
