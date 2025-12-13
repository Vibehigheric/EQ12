#!/usr/bin/env python3
"""
EQ12 BOOLEAN LOGIC ENGINE - SPORTS BETTING AUTOMATION
====================================================
Advanced Boolean logic implementation for EQ12 parlay generation and betting decisions.
Integrates with NCAA Week 7 conference system and live betting operations.

Author: EQ12 Team
Date: October 4, 2025
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# EQ12 System imports
from eq12_error_boundary import GPT5ErrorBoundary
from eq12_unicode_simple import safe_print


class AccessLevel(Enum):
    """User access levels for Boolean logic evaluation."""

    GUEST = "guest"
    STANDARD = "standard"
    VIP = "vip"
    ADMIN = "admin"
    SYSTEM = "system"


class BettingState(Enum):
    """System betting states for Boolean evaluation."""

    CLOSED = "closed"
    OPEN = "open"
    RESTRICTED = "restricted"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"


@dataclass
class SystemConditions:
    """Boolean conditions for EQ12 betting system state."""

    user_logged_in: bool = False
    has_admin_rights: bool = False
    has_vip_access: bool = False
    betting_window_open: bool = False
    maintenance_mode: bool = False
    sufficient_bankroll: bool = False
    game_started: bool = False
    live_odds_available: bool = False
    emergency_override: bool = False
    api_keys_valid: bool = False

    # EQ12 specific conditions
    ncaa_week7_active: bool = False
    parlay_generation_enabled: bool = False
    conference_data_loaded: bool = False
    sentiment_analysis_ready: bool = False


class EQ12BooleanLogicEngine:
    """
    Professional Boolean logic engine for EQ12 sports betting automation.
    Implements complex decision trees using AND, OR, NOT, XOR operators.
    """

    def __init__(self, eq12_root: str = "C:\\EQ12"):
        self.eq12_root = eq12_root
        self.error_boundary = GPT5ErrorBoundary()
        self.logger = self._setup_logging()

        # Initialize system state
        self.conditions = SystemConditions()
        self.decision_cache = {}
        self.access_level = AccessLevel.GUEST

        safe_print("🔧 EQ12 Boolean Logic Engine initialized")
        self.logger.info("Boolean Logic Engine startup complete")

    def _setup_logging(self) -> logging.Logger:
        """Set up logging for Boolean logic operations."""
        logger = logging.getLogger("EQ12BooleanLogic")
        handler = logging.FileHandler(f"{self.eq12_root}\\logs\\boolean_logic.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def update_system_state(self, **kwargs) -> None:
        """Update system conditions for Boolean evaluation."""
        for key, value in kwargs.items():
            if hasattr(self.conditions, key):
                setattr(self.conditions, key, value)
                self.logger.info(f"Updated condition: {key} = {value}")

    def demonstrate_and_operator(self) -> dict[str, bool]:
        """
        Demonstrate AND operator - ALL conditions must be True.
        Critical for security and risk management in betting systems.
        """
        safe_print("\n🔒 AND OPERATOR DEMONSTRATION")
        safe_print("=" * 50)

        results = {}

        # 1. Admin betting access (requires login AND admin rights)
        admin_betting = self.conditions.user_logged_in and self.conditions.has_admin_rights
        results["admin_betting"] = admin_betting

        status = "✅ GRANTED" if admin_betting else "❌ DENIED"
        safe_print(f"Admin Betting Access: {status}")
        if not admin_betting:
            missing = []
            if not self.conditions.user_logged_in:
                missing.append("Login")
            if not self.conditions.has_admin_rights:
                missing.append("Admin Rights")
            safe_print(f"   Missing: {', '.join(missing)}")

        # 2. Standard parlay placement (multiple AND conditions)
        parlay_placement = (
            self.conditions.user_logged_in
            and self.conditions.betting_window_open
            and self.conditions.sufficient_bankroll
            and not self.conditions.maintenance_mode
            and self.conditions.api_keys_valid
        )

        results["parlay_placement"] = parlay_placement
        status = "✅ AUTHORIZED" if parlay_placement else "❌ BLOCKED"
        safe_print(f"Parlay Placement: {status}")

        # 3. NCAA Week 7 system ready (EQ12 specific)
        ncaa_system_ready = (
            self.conditions.ncaa_week7_active
            and self.conditions.conference_data_loaded
            and self.conditions.sentiment_analysis_ready
            and self.conditions.live_odds_available
        )

        results["ncaa_system_ready"] = ncaa_system_ready
        status = "✅ READY" if ncaa_system_ready else "❌ NOT READY"
        safe_print(f"NCAA Week 7 System: {status}")

        self.logger.info(f"AND operator results: {results}")
        return results

    def demonstrate_or_operator(self) -> dict[str, bool]:
        """
        Demonstrate OR operator - ANY condition can grant access.
        Used for flexible access control and emergency overrides.
        """
        safe_print("\n🚪 OR OPERATOR DEMONSTRATION")
        safe_print("=" * 50)

        results = {}

        # 1. Betting access (window open OR admin override OR VIP access)
        betting_access = (
            self.conditions.betting_window_open
            or self.conditions.has_admin_rights
            or self.conditions.has_vip_access
            or self.conditions.emergency_override
        )

        results["betting_access"] = betting_access
        status = "✅ ALLOWED" if betting_access else "❌ DENIED"
        safe_print(f"Betting Access: {status}")

        if betting_access:
            reasons = []
            if self.conditions.betting_window_open:
                reasons.append("Window Open")
            if self.conditions.has_admin_rights:
                reasons.append("Admin Override")
            if self.conditions.has_vip_access:
                reasons.append("VIP Access")
            if self.conditions.emergency_override:
                reasons.append("Emergency Override")
            safe_print(f"   Granted via: {', '.join(reasons)}")

        # 2. Live betting availability
        live_betting = (
            self.conditions.game_started
            or self.conditions.live_odds_available
            or self.conditions.has_admin_rights
        )

        results["live_betting"] = live_betting
        status = "✅ AVAILABLE" if live_betting else "❌ UNAVAILABLE"
        safe_print(f"Live Betting: {status}")

        # 3. Data source availability (backup systems)
        data_available = (
            self.conditions.live_odds_available
            or self.conditions.conference_data_loaded
            or self.conditions.sentiment_analysis_ready
        )

        results["data_available"] = data_available
        status = "✅ OPERATIONAL" if data_available else "❌ NO DATA"
        safe_print(f"Data Sources: {status}")

        self.logger.info(f"OR operator results: {results}")
        return results

    def demonstrate_not_operator(self) -> dict[str, bool]:
        """
        Demonstrate NOT operator - Logical inversion.
        Critical for safety checks and inverse conditions.
        """
        safe_print("\n🔄 NOT OPERATOR DEMONSTRATION")
        safe_print("=" * 50)

        results = {}

        # 1. System operational (NOT in maintenance)
        system_operational = not self.conditions.maintenance_mode
        results["system_operational"] = system_operational

        status = "✅ OPERATIONAL" if system_operational else "⚠️ MAINTENANCE"
        safe_print(f"System Status: {status}")

        # 2. Betting window status (NOT closed)
        window_open = bool(self.conditions.betting_window_open)  # Double negative example
        results["window_status"] = window_open

        status = "✅ OPEN" if window_open else "❌ CLOSED"
        safe_print(f"Betting Window: {status}")

        # 3. Security check (NOT admin attempting admin functions)
        security_violation = (
            self.conditions.user_logged_in
            and not self.conditions.has_admin_rights
            and self.conditions.has_vip_access
        )  # VIP trying admin functions

        results["security_check"] = not security_violation
        status = "✅ SECURE" if not security_violation else "⚠️ VIOLATION"
        safe_print(f"Security Status: {status}")

        # 4. Risk management (NOT exceeding limits)
        within_limits = not (
            self.conditions.sufficient_bankroll
            and not self.conditions.has_vip_access
            and self.conditions.betting_window_open
        )  # High risk scenario

        results["risk_managed"] = within_limits
        status = "✅ SAFE" if within_limits else "⚠️ HIGH RISK"
        safe_print(f"Risk Level: {status}")

        self.logger.info(f"NOT operator results: {results}")
        return results

    def demonstrate_xor_operator(self) -> dict[str, bool]:
        """
        Demonstrate XOR operator - Exactly ONE condition must be True.
        Used for exclusive states and security validation.
        """
        safe_print("\n⚖️ XOR OPERATOR DEMONSTRATION")
        safe_print("=" * 50)

        results = {}

        # 1. Exclusive access control (Admin XOR VIP, not both for security)
        exclusive_access = self.conditions.has_admin_rights ^ self.conditions.has_vip_access
        results["exclusive_access"] = exclusive_access

        if self.conditions.has_admin_rights and self.conditions.has_vip_access:
            safe_print("⚠️ SECURITY ALERT: Both Admin and VIP active")
        elif exclusive_access:
            access_type = "Admin" if self.conditions.has_admin_rights else "VIP"
            safe_print(f"✅ Exclusive Access: {access_type} only")
        else:
            safe_print("❌ No special access granted")

        # 2. System state validation (Maintenance XOR Normal operation)
        valid_state = self.conditions.maintenance_mode ^ (
            self.conditions.betting_window_open and self.conditions.parlay_generation_enabled
        )
        results["valid_system_state"] = valid_state

        status = "✅ VALID" if valid_state else "⚠️ CONFLICTED"
        safe_print(f"System State: {status}")

        # 3. Data source priority (Live odds XOR Historical data, not both for efficiency)
        data_priority = self.conditions.live_odds_available ^ self.conditions.conference_data_loaded
        results["data_priority"] = data_priority

        if data_priority:
            source = "Live Odds" if self.conditions.live_odds_available else "Historical Data"
            safe_print(f"✅ Data Source: {source} (exclusive)")
        else:
            safe_print("⚠️ Data Source: Conflict or neither available")

        self.logger.info(f"XOR operator results: {results}")
        return results

    def complex_parlay_validation(self) -> dict[str, any]:
        """
        Complex Boolean logic for EQ12 parlay validation and placement.
        Combines multiple operators for sophisticated decision making.
        """
        safe_print("\n🎯 COMPLEX PARLAY VALIDATION LOGIC")
        safe_print("=" * 50)

        results = {}

        # 1. Parlay Authorization Matrix
        parlay_authorized = (
            (
                self.conditions.user_logged_in
                and self.conditions.sufficient_bankroll
                and self.conditions.betting_window_open
            )
            and not self.conditions.maintenance_mode
            and (self.conditions.live_odds_available or self.conditions.has_admin_rights)
        )

        results["parlay_authorized"] = parlay_authorized
        status = "✅ AUTHORIZED" if parlay_authorized else "❌ BLOCKED"
        safe_print(f"Parlay Authorization: {status}")

        # 2. Risk Assessment Logic
        high_risk = (
            not self.conditions.has_vip_access and self.conditions.sufficient_bankroll
        ) or (
            self.conditions.has_admin_rights
            and self.conditions.betting_window_open
            and not self.conditions.maintenance_mode
        )

        results["high_risk_detected"] = high_risk
        if high_risk:
            safe_print("⚠️ High Risk Betting: Enhanced monitoring enabled")

        # 3. NCAA Week 7 Conference Logic
        ncaa_ready = (
            self.conditions.ncaa_week7_active
            and self.conditions.conference_data_loaded
            and self.conditions.sentiment_analysis_ready
            and (self.conditions.live_odds_available or self.conditions.has_admin_rights)
            and not (self.conditions.maintenance_mode and not self.conditions.emergency_override)
        )

        results["ncaa_week7_ready"] = ncaa_ready
        status = "✅ READY" if ncaa_ready else "❌ NOT READY"
        safe_print(f"NCAA Week 7 System: {status}")

        # 4. Emergency Access Protocol
        emergency_access = (
            self.conditions.has_admin_rights
            and (self.conditions.maintenance_mode or not self.conditions.betting_window_open)
            and self.conditions.api_keys_valid
        )

        results["emergency_access"] = emergency_access
        if emergency_access:
            safe_print("🚨 Emergency Access: Admin override protocols active")

        # 5. Automated Decision Score
        decision_factors = [
            parlay_authorized,
            not high_risk,
            ncaa_ready,
            self.conditions.api_keys_valid,
            not self.conditions.maintenance_mode,
        ]

        decision_score = sum(decision_factors) / len(decision_factors)
        results["decision_score"] = decision_score

        if decision_score >= 0.8:
            decision = "✅ PROCEED WITH CONFIDENCE"
        elif decision_score >= 0.6:
            decision = "⚠️ PROCEED WITH CAUTION"
        elif decision_score >= 0.4:
            decision = "🔍 MANUAL REVIEW REQUIRED"
        else:
            decision = "❌ SYSTEM HOLD - DO NOT PROCEED"

        safe_print(f"Automated Decision: {decision} (Score: {decision_score:.2%})")
        results["final_decision"] = decision

        self.logger.info(f"Complex validation results: {results}")
        return results

    def run_comprehensive_demo(self) -> dict[str, any]:
        """Run complete Boolean logic demonstration for EQ12 system."""
        safe_print("🏈 EQ12 BOOLEAN LOGIC ENGINE - COMPREHENSIVE DEMONSTRATION")
        safe_print("=" * 65)

        # Set example conditions
        self.update_system_state(
            user_logged_in=True,
            has_admin_rights=False,
            has_vip_access=False,
            betting_window_open=True,
            maintenance_mode=False,
            sufficient_bankroll=True,
            game_started=False,
            live_odds_available=True,
            emergency_override=False,
            api_keys_valid=True,
            ncaa_week7_active=True,
            parlay_generation_enabled=True,
            conference_data_loaded=True,
            sentiment_analysis_ready=True,
        )

        safe_print("\n📊 Current System State:")
        for key, value in self.conditions.__dict__.items():
            emoji = "✅" if value else "❌"
            safe_print(f"   {emoji} {key.replace('_', ' ').title()}: {value}")

        # Run all demonstrations
        and_results = self.demonstrate_and_operator()
        or_results = self.demonstrate_or_operator()
        not_results = self.demonstrate_not_operator()
        xor_results = self.demonstrate_xor_operator()
        complex_results = self.complex_parlay_validation()

        # Summary
        safe_print("\n🏆 DEMONSTRATION COMPLETE")
        safe_print("=" * 50)
        safe_print("💡 Boolean Logic Applications in EQ12:")
        safe_print("   • Security & Access Control (AND/OR combinations)")
        safe_print("   • Risk Management (NOT operators)")
        safe_print("   • Exclusive State Management (XOR)")
        safe_print("   • Complex Decision Trees (Multi-operator logic)")
        safe_print("   • Automated Parlay Validation")
        safe_print("   • NCAA Conference System Integration")

        # Compile comprehensive results
        comprehensive_results = {
            "timestamp": datetime.now().isoformat(),
            "system_conditions": self.conditions.__dict__.copy(),
            "and_operations": and_results,
            "or_operations": or_results,
            "not_operations": not_results,
            "xor_operations": xor_results,
            "complex_validation": complex_results,
        }

        # Save results to JSON
        results_path = f"{self.eq12_root}\\outputs\\boolean_logic_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            os.makedirs(os.path.dirname(results_path), exist_ok=True)
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)
            safe_print(f"\n💾 Results saved to: {results_path}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")

        return comprehensive_results


def main():
    """Main execution function for Boolean logic demonstration."""
    try:
        # Initialize Boolean Logic Engine
        engine = EQ12BooleanLogicEngine()

        # Run comprehensive demonstration
        results = engine.run_comprehensive_demo()

        safe_print("\n✨ EQ12 Boolean Logic Engine demonstration completed successfully!")
        safe_print(
            f"📈 Total operations evaluated: {len(results) - 2}"
        )  # Exclude timestamp and conditions

        return results

    except Exception as e:
        logging.error(f"Boolean logic demonstration failed: {e}")
        safe_print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    main()
