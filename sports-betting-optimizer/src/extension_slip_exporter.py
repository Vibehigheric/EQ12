#!/usr/bin/env python3
"""
Extension Slip Exporter for Sports Betting Optimizer
Automatically exports best parlays to bridge format for browser extension
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ExtensionSlipExporter:
    """Exports optimizer results to bridge format for browser extension"""

    def __init__(self, bridge_path: str | None = None):
        """
        Initialize exporter with bridge directory path

        Args:
            bridge_path: Path to betting-bridge directory.
                        Auto-detects if None.
        """
        self.bridge_path = self._find_bridge_path(bridge_path)
        self.export_dir = self.bridge_path / "data" / "parlays"

        # Ensure export directory exists
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def _find_bridge_path(self, provided_path: str | None = None) -> Path:
        """Find or create bridge directory"""
        if provided_path:
            return Path(provided_path)

        # Look in common locations relative to optimizer
        current_dir = Path.cwd()
        search_paths = [
            current_dir / "betting-bridge",
            current_dir.parent / "betting-bridge",
            current_dir / ".." / "betting-bridge",
            current_dir / "sports-betting-extension" / "betting-bridge",
        ]

        # Check existing paths
        for path in search_paths:
            if path.exists():
                return path.resolve()

        # Create default location
        default_path = current_dir / "betting-bridge"
        default_path.mkdir(exist_ok=True)
        (default_path / "data" / "parlays").mkdir(parents=True, exist_ok=True)

        return default_path

    def export_parlay(
        self,
        optimizer_result: dict[str, Any],
        sport: str,
        promo_type: str,
        promo_date: str,
    ) -> dict[str, Any]:
        """
        Export optimizer result to extension bridge format

        Args:
            optimizer_result: Result dict from master_optimizer
            sport: Sport name (nfl, cfb, nba, etc.)
            promo_type: Promo type (mystery, stepped)
            promo_date: Date string (YYYY-MM-DD)

        Returns:
            Formatted slip data that was written
        """

        # Generate unique slip ID
        slip_id = f"{promo_date}-{sport}-{promo_type}"

        # Extract legs data
        legs = []
        for leg in optimizer_result.get("legs", []):
            leg_data = {
                "label": getattr(leg, "label", str(leg)),
                "american": getattr(leg, "american", 0),
                "game": getattr(leg, "game", "Unknown"),
            }
            legs.append(leg_data)

        # Build extension-compatible slip
        slip_data = {
            "id": slip_id,
            "sport": sport,
            "ev": round(optimizer_result.get("ev", 0), 2),
            "stake": optimizer_result.get("stake", 100),
            "legs": legs,
            "promo_type": promo_type,
            "promo_date": promo_date,
            "combined_odds": optimizer_result.get("combined_american", 0),
            "p_win": round(optimizer_result.get("p_win", 0) * 100, 2),
            "boosted_payout": round(optimizer_result.get("boosted_payout", 0), 2),
            "boost_percentage": optimizer_result.get("boost_pct", 0),
            "timestamp": datetime.now(UTC).isoformat(),
            "legs_count": len(legs),
        }

        # Write to latest.json (picked up by extension)
        latest_file = self.export_dir / "latest.json"
        with open(latest_file, "w") as f:
            json.dump(slip_data, f, indent=2)

        # Also save timestamped version for history
        timestamped_file = self.export_dir / f"{slip_id}.json"
        with open(timestamped_file, "w") as f:
            json.dump(slip_data, f, indent=2)

        print(f"📱 Extension slip exported: {latest_file}")
        print(
            f"   → {len(legs)} legs | EV: ${slip_data['ev']:.2f} | Payout: ${slip_data['boosted_payout']:.2f}"
        )

        return slip_data

    def export_from_args_and_result(self, args, best_result: dict[str, Any]) -> dict[str, Any]:
        """
        Convenience method to export using argparse args and optimizer result

        Args:
            args: argparse Namespace from master_optimizer
            best_result: Best parlay result dict

        Returns:
            Formatted slip data
        """
        return self.export_parlay(
            optimizer_result=best_result,
            sport=args.sport,
            promo_type=args.promo,
            promo_date=args.promo_date,
        )


def patch_master_optimizer():
    """
    Monkey patch master_optimizer.py to automatically export extension slips
    Call this at the top of your main() function
    """
    try:
        # Create exporter instance
        exporter = ExtensionSlipExporter()

        # Store in global for access
        globals()["_EXTENSION_EXPORTER"] = exporter

        print("✅ Extension slip exporter initialized")
        print(f"📁 Bridge path: {exporter.bridge_path}")

        return exporter

    except Exception as e:
        print(f"⚠️  Extension exporter setup failed: {e}")
        return None


def export_best_parlay(args, best_result: dict[str, Any]) -> bool:
    """
    Export the best parlay result to extension format
    Call this after finding your best parlay

    Args:
        args: Command line arguments from master_optimizer
        best_result: Best parlay result dictionary

    Returns:
        True if export successful, False otherwise
    """
    try:
        exporter = globals().get("_EXTENSION_EXPORTER")

        if not exporter:
            exporter = ExtensionSlipExporter()

        exporter.export_from_args_and_result(args, best_result)
        return True

    except Exception as e:
        print(f"⚠️  Extension export failed: {e}")
        return False


# Direct integration example for your master_optimizer.py
INTEGRATION_CODE = """
# Add this to the top of your master_optimizer.py after imports:
try:
    from .extension_slip_exporter import patch_master_optimizer, export_best_parlay
    EXTENSION_EXPORT = True
except ImportError:
    try:
        # Fallback if running from different directory
        import sys, os
        sys.path.append(os.path.dirname(__file__))
        from extension_slip_exporter import patch_master_optimizer, export_best_parlay
        EXTENSION_EXPORT = True
    except ImportError:
        EXTENSION_EXPORT = False
        def patch_master_optimizer(): return None
        def export_best_parlay(args, result): return False

# At the start of your run() function, add:
if EXTENSION_EXPORT:
    patch_master_optimizer()

# After finding your best parlay (line ~96), add:
if EXTENSION_EXPORT and best is not None:
    export_best_parlay(args, best)
"""

if __name__ == "__main__":
    # Test the exporter with mock data
    exporter = ExtensionSlipExporter()

    # Mock optimizer result
    mock_leg_1 = type("Leg", (), {"label": "Chiefs -3.5", "american": -110, "game": "KC @ DEN"})()

    mock_leg_2 = type("Leg", (), {"label": "Over 45.5", "american": -105, "game": "KC @ DEN"})()

    mock_result = {
        "legs": [mock_leg_1, mock_leg_2],
        "ev": 12.34,
        "stake": 100,
        "combined_american": 264,
        "p_win": 0.3785,
        "boosted_payout": 425.0,
        "boost_pct": 25,
    }

    # Test export
    slip_data = exporter.export_parlay(
        optimizer_result=mock_result,
        sport="nfl",
        promo_type="mystery",
        promo_date="2025-10-03",
    )

    print("\n📋 Integration code ready!")
    print("Add to your master_optimizer.py:")
    print(INTEGRATION_CODE)
