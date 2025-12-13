#!/usr/bin/env python3
"""
Direct Optimizer Integration
Patches existing master_optimizer.py to push parlays directly to extension via WebSocket
"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

import websockets


class OptimizerExtensionHook:
    """Hooks into existing optimizer to push parlays directly to extension"""

    def __init__(self):
        self.websocket_url = "ws://localhost:8765"

    async def push_parlay_to_extension(self, parlay_data: dict[str, Any]):
        """Push generated parlay directly to extension"""
        try:
            async with websockets.connect(self.websocket_url, timeout=5) as ws:
                message = {
                    "type": "new_parlay",
                    "parlay": parlay_data,
                    "source": "optimizer_direct",
                    "timestamp": datetime.now(UTC).isoformat(),
                }

                await ws.send(json.dumps(message))
                print(f"📱 Parlay pushed to extension: {len(parlay_data.get('legs', []))} legs")

        except Exception as e:
            print(f"⚠️  Extension push failed: {e}")
            # Continue normally if extension not available

    def format_parlay_for_extension(self, parlay_result: dict[str, Any]) -> dict[str, Any]:
        """Convert optimizer output to extension-friendly format"""
        return {
            "sport": parlay_result.get("sport", "nfl"),
            "promo_type": parlay_result.get("promo_type", "mystery"),
            "ev": f"+{parlay_result.get('expected_value', 0):.1f}%",
            "stake": parlay_result.get("stake", 100),
            "legs": [
                {
                    "label": leg.get("description", "Unknown"),
                    "odds": leg.get("odds", "+100"),
                    "market": leg.get("market_type", "unknown"),
                }
                for leg in parlay_result.get("legs", [])
            ],
            "boost_percentage": parlay_result.get("boost_percentage", 0),
            "potential_payout": f"${parlay_result.get('potential_payout', 0):.0f}",
            "timestamp": datetime.now(UTC).isoformat(),
            "confidence": parlay_result.get("confidence", "medium"),
        }

    def patch_master_optimizer(self):
        """Monkey patch the master optimizer to include extension push"""
        try:
            import sys

            sys.path.append("../sports-betting-optimizer/src")

            from promos import master_optimizer

            # Store original function
            original_save_results = getattr(master_optimizer, "save_parlay_results", None)

            def enhanced_save_results(parlay_data):
                """Enhanced save that also pushes to extension"""
                # Call original save function
                if original_save_results:
                    result = original_save_results(parlay_data)
                else:
                    result = parlay_data

                # Format and push to extension
                extension_data = self.format_parlay_for_extension(parlay_data)

                # Push asynchronously without blocking main optimizer
                asyncio.create_task(self.push_parlay_to_extension(extension_data))

                return result

            # Patch the function
            master_optimizer.save_parlay_results = enhanced_save_results
            print("✅ Master optimizer patched for extension integration")

        except ImportError:
            print("⚠️  Could not patch optimizer - module not found")
        except Exception as e:
            print(f"⚠️  Patch failed: {e}")


# Standalone function to push any parlay to extension
async def push_parlay(parlay_data: dict[str, Any], websocket_url: str = "ws://localhost:8765"):
    """Standalone function to push parlay to extension"""
    try:
        async with websockets.connect(websocket_url, timeout=3) as ws:
            message = {
                "type": "new_parlay",
                "parlay": parlay_data,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            await ws.send(json.dumps(message))
            return True
    except Exception:
        return False


# Integration example for existing optimizer scripts
def integrate_with_existing_optimizer():
    """Example integration with existing optimizer"""

    # Add this to your existing master_optimizer.py:
    """
    # At the top of master_optimizer.py, add:
    try:
        from optimizer_extension_hook import push_parlay
        EXTENSION_AVAILABLE = True
    except ImportError:
        EXTENSION_AVAILABLE = False

    # In your parlay generation function, after finding best parlay:
    if EXTENSION_AVAILABLE and best_parlay:
        extension_data = {
            "sport": args.sport,
            "promo_type": args.promo,
            "ev": f"+{best_parlay['ev']:.1f}%",
            "stake": args.stake,
            "legs": [
                {"label": leg["description"], "odds": leg["odds"], "market": leg["type"]}
                for leg in best_parlay["legs"]
            ],
            "boost_percentage": best_parlay.get("boost", 0),
            "potential_payout": f"${best_parlay['payout']:.0f}"
        }

        # Push to extension (non-blocking)
        try:
            import asyncio
            asyncio.create_task(push_parlay(extension_data))
        except Exception:
            pass  # Continue if extension not available
    """

    print("📋 Integration code ready - add to your master_optimizer.py")


if __name__ == "__main__":
    # Test the integration
    hook = OptimizerExtensionHook()

    # Test parlay data
    test_parlay = {
        "sport": "nfl",
        "promo_type": "mystery",
        "expected_value": 12.5,
        "stake": 100,
        "legs": [
            {"description": "Chiefs -3.5", "odds": "-110", "market_type": "spread"},
            {"description": "Over 45.5", "odds": "-105", "market_type": "total"},
        ],
        "boost_percentage": 25,
        "potential_payout": 425,
    }

    # Test push
    async def test():
        await hook.push_parlay_to_extension(hook.format_parlay_for_extension(test_parlay))

    asyncio.run(test())
