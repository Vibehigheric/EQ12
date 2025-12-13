"""
EQ12 Parlay Validation System
Ensures all parlays are sportsbook-compliant and actually placeable
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class ValidationResult:
    """Result of parlay validation"""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    fixed_parlay: dict[str, Any] = None


class ParlayValidator:
    """Validates parlay tickets for real sportsbook compliance"""

    ALLOWED_SPORTSBOOKS = {"DraftKings", "FanDuel", "BetMGM"}

    # Markets that conflict with each other in the same game
    CONFLICTING_MARKETS = {
        ("Total", "Over"): ("Total", "Under"),
        ("Total", "Under"): ("Total", "Over"),
        ("Moneyline"): None,  # Can't have both sides of ML in same game
        ("Spread"): None,  # Can't have both sides of spread in same game
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_parlay_set(self, parlay_data: dict[str, Any]) -> dict[str, Any]:
        """Validate entire set of parlays and fix issues"""
        results = {
            "original_parlays": len(parlay_data.get("parlays", [])),
            "valid_parlays": [],
            "invalid_parlays": [],
            "validation_errors": [],
            "fixes_applied": [],
        }

        for i, parlay in enumerate(parlay_data.get("parlays", [])):
            validation = self.validate_single_parlay(parlay)

            if validation.is_valid:
                results["valid_parlays"].append(parlay)
            else:
                results["invalid_parlays"].append(
                    {
                        "index": i,
                        "strategy": parlay.get("strategy", "Unknown"),
                        "errors": validation.errors,
                        "warnings": validation.warnings,
                    }
                )

                # Try to fix the parlay
                if validation.fixed_parlay:
                    results["valid_parlays"].append(validation.fixed_parlay)
                    results["fixes_applied"].append(f"Fixed parlay {i}: {parlay.get('strategy')}")

        return results

    def validate_single_parlay(self, parlay: dict[str, Any]) -> ValidationResult:
        """Validate a single parlay for sportsbook compliance"""
        errors = []
        warnings = []
        legs = parlay.get("legs", [])

        if not legs:
            errors.append("Parlay has no legs")
            return ValidationResult(False, errors, warnings)

        # Check 1: Single sportsbook per parlay
        sportsbooks = {leg.get("sportsbook") for leg in legs}
        if len(sportsbooks) > 1:
            errors.append(f"Multiple sportsbooks in one parlay: {sportsbooks}")

        # Check 2: Only allowed sportsbooks
        invalid_books = sportsbooks - self.ALLOWED_SPORTSBOOKS
        if invalid_books:
            errors.append(f"Invalid sportsbooks: {invalid_books}")

        # Check 3: No duplicate game selections
        game_selections = self._get_game_selections(legs)
        duplicates = self._find_duplicate_selections(game_selections)
        if duplicates:
            errors.append(f"Duplicate/conflicting selections: {duplicates}")

        # Check 4: Reasonable odds and payouts
        odds_issues = self._validate_odds_and_payouts(parlay)
        if odds_issues:
            warnings.extend(odds_issues)

        # Check 5: Valid timestamps
        timestamp_issues = self._validate_timestamps(legs)
        if timestamp_issues:
            warnings.extend(timestamp_issues)

        # Try to create a fixed version if there are fixable errors
        fixed_parlay = None
        if errors and self._can_fix_errors(errors):
            fixed_parlay = self._attempt_fix(parlay, errors)

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, fixed_parlay)

    def _get_game_selections(self, legs: list[dict[str, Any]]) -> list[tuple[str, str, str]]:
        """Get (game_id, market, selection) tuples for conflict detection"""
        return [
            (leg.get("game_id", ""), leg.get("market", ""), leg.get("selection", ""))
            for leg in legs
        ]

    def _find_duplicate_selections(self, selections: list[tuple[str, str, str]]) -> list[str]:
        """Find duplicate or conflicting selections in the same game"""
        game_markets = defaultdict(list)
        duplicates = []

        for game_id, market, selection in selections:
            if not game_id:
                continue
            game_markets[game_id].append((market, selection))

        for game_id, markets in game_markets.items():
            if len(markets) > 1:
                # Check for same market, different selections (conflicting)
                market_selections = defaultdict(list)
                for market, selection in markets:
                    market_selections[market].append(selection)

                for market, sels in market_selections.items():
                    if len(sels) > 1:
                        duplicates.append(f"{game_id}: {market} has {sels}")

                    # Check for conflicting Over/Under in same game
                    if market == "Total":
                        over_count = sum(1 for s in sels if "Over" in s)
                        under_count = sum(1 for s in sels if "Under" in s)
                        if over_count > 0 and under_count > 0:
                            duplicates.append(f"{game_id}: Both Over and Under selected")

        return duplicates

    def _validate_odds_and_payouts(self, parlay: dict[str, Any]) -> list[str]:
        """Validate odds calculations and payout reasonableness"""
        warnings = []

        multiplier = parlay.get("multiplier", 0)
        potential_payout = parlay.get("potential_payout", 0)
        recommended_stake = parlay.get("recommended_stake", 0)

        # Check for astronomical payouts (usually indicates duplicate legs)
        if multiplier > 1000:
            warnings.append(f"Extremely high multiplier ({multiplier}x) - likely invalid")

        if potential_payout > recommended_stake * 200:
            warnings.append(f"Payout seems too high: ${potential_payout} on ${recommended_stake}")

        # Verify payout calculation
        if recommended_stake > 0:
            expected_payout = recommended_stake * multiplier
            if abs(expected_payout - potential_payout) > 1.0:
                warnings.append(
                    f"Payout calculation mismatch: expected ${expected_payout}, got ${potential_payout}"
                )

        return warnings

    def _validate_timestamps(self, legs: list[dict[str, Any]]) -> list[str]:
        """Validate game commence times using eq12_time and eq12_windows helpers"""
        from eq12_time import now_utc, parse_ts
        from eq12_windows import LOCK_BUFFER

        warnings = []
        now = now_utc()

        for leg in legs:
            commence_str = leg.get("commence_time", "")
            if not commence_str:
                warnings.append(f"Missing commence_time for {leg.get('game_id', 'unknown game')}")
                continue

            try:
                commence_time = parse_ts(commence_str)
                # Exclude legs that have started or are inside lock buffer
                if commence_time <= now + LOCK_BUFFER:
                    warnings.append(
                        f"Game already started or locked: {leg.get('game_id')} at {commence_str}"
                    )
            except Exception:
                warnings.append(f"Invalid timestamp format: {commence_str}")

        return warnings

    def _can_fix_errors(self, errors: list[str]) -> bool:
        """Check if errors are fixable automatically"""
        fixable_patterns = [
            "Multiple sportsbooks",
            "Duplicate/conflicting selections",
            "Invalid sportsbooks",
        ]

        return any(any(pattern in error for pattern in fixable_patterns) for error in errors)

    def _attempt_fix(self, parlay: dict[str, Any], errors: list[str]) -> dict[str, Any]:
        """Attempt to fix common parlay errors"""
        fixed_parlay = parlay.copy()
        legs = fixed_parlay.get("legs", [])

        # Fix 1: Single sportsbook - use most common sportsbook
        if "Multiple sportsbooks" in str(errors):
            sportsbook_counts = defaultdict(int)
            for leg in legs:
                book = leg.get("sportsbook")
                if book in self.ALLOWED_SPORTSBOOKS:
                    sportsbook_counts[book] += 1

            if sportsbook_counts:
                primary_book = max(sportsbook_counts, key=sportsbook_counts.get)
                fixed_legs = [leg for leg in legs if leg.get("sportsbook") == primary_book]
                fixed_parlay["legs"] = fixed_legs
                fixed_parlay["strategy"] += f" (Fixed: {primary_book} only)"

        # Fix 2: Remove duplicates - keep first occurrence per game
        if "Duplicate/conflicting" in str(errors):
            seen_games = set()
            clean_legs = []

            for leg in fixed_parlay["legs"]:
                game_id = leg.get("game_id")
                if game_id not in seen_games:
                    clean_legs.append(leg)
                    seen_games.add(game_id)

            fixed_parlay["legs"] = clean_legs
            fixed_parlay["strategy"] += " (Duplicates removed)"

        # Recalculate odds and payouts for fixed parlay
        if len(fixed_parlay["legs"]) != len(parlay["legs"]):
            fixed_parlay = self._recalculate_parlay_odds(fixed_parlay)

        return fixed_parlay

    def _recalculate_parlay_odds(self, parlay: dict[str, Any]) -> dict[str, Any]:
        """Recalculate parlay odds after fixing legs"""
        legs = parlay.get("legs", [])
        if not legs:
            return parlay

        # Convert American odds to decimal and multiply
        total_decimal_odds = 1.0
        for leg in legs:
            american_odds = leg.get("odds", -110)
            if american_odds > 0:
                decimal_odds = (american_odds / 100) + 1
            else:
                decimal_odds = (100 / abs(american_odds)) + 1
            total_decimal_odds *= decimal_odds

        # Convert back to American odds
        if total_decimal_odds >= 2.0:
            american_odds = int((total_decimal_odds - 1) * 100)
        else:
            american_odds = int(-100 / (total_decimal_odds - 1))

        # Update parlay values
        parlay["leg_count"] = len(legs)
        parlay["american_odds"] = american_odds
        parlay["multiplier"] = round(total_decimal_odds, 2)

        stake = parlay.get("recommended_stake", 25)
        parlay["potential_payout"] = round(stake * total_decimal_odds, 2)
        parlay["net_profit"] = round(parlay["potential_payout"] - stake, 2)

        return parlay


def validate_parlay_file(file_path: str) -> dict[str, Any]:
    """Validate parlays from JSON file and save cleaned version"""
    validator = ParlayValidator()

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load file: {e}"}

    # Validate the parlays
    validation_results = validator.validate_parlay_set(data)

    # Create cleaned data file
    if validation_results["valid_parlays"]:
        cleaned_data = data.copy()
        cleaned_data["parlays"] = validation_results["valid_parlays"]
        cleaned_data["validation_status"] = "✅ VALIDATED"
        cleaned_data["validation_timestamp"] = datetime.now(UTC).isoformat()
        cleaned_data["validation_summary"] = {
            "original_count": validation_results["original_parlays"],
            "valid_count": len(validation_results["valid_parlays"]),
            "invalid_count": len(validation_results["invalid_parlays"]),
            "fixes_applied": validation_results["fixes_applied"],
        }

        # Save cleaned version
        clean_path = file_path.replace(".json", "_validated.json")
        with open(clean_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

        validation_results["cleaned_file"] = clean_path

    return validation_results


if __name__ == "__main__":
    # Test with the clean parlay file
    import os

    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # Validate the clean parlay file
    clean_file = "C:/EQ12/logs/nfl_parlays_clean_20251005_placeable.json"

    if os.path.exists(clean_file):
        print(f"🔍 Validating clean parlay file: {clean_file}")
        results = validate_parlay_file(clean_file)

        print("✅ Validation complete:")
        print(f"   Valid parlays: {len(results.get('valid_parlays', []))}")
        print(f"   Invalid parlays: {len(results.get('invalid_parlays', []))}")

        if results.get("invalid_parlays"):
            print("\n❌ Issues found:")
            for invalid in results["invalid_parlays"]:
                print(f"   - {invalid['strategy']}: {invalid['errors']}")

        if results.get("cleaned_file"):
            print(f"\n📁 Cleaned file saved: {results['cleaned_file']}")
    else:
        print(f"❌ File not found: {clean_file}")
        print("Run this script from the EQ12 directory")
