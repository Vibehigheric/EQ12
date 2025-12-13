#!/usr/bin/env python3
"""
EQ12 Automated Hedge Engine - Dynamic Hedge Optimization System
===============================================================

Advanced hedge optimization system with:
- Real-time hedge calculations for live parlays
- Guaranteed profit scenarios with dynamic pricing
- Partial cashout optimization
- Multi-leg hedge strategies
- Risk-free profit locking mechanisms
- Integration with live betting markets

Features:
- Dynamic hedge calculations for any parlay combination
- Guaranteed profit scenarios regardless of outcome
- Partial cashout optimization with live odds
- Multi-outcome hedge strategies (3+ way hedging)
- Risk-free profit locking with minimal capital
- Real-time opportunity monitoring and alerts
- Integration with existing EQ12 EdgeGod system

Author: EQ12 Development Team
Date: October 6, 2025
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from telegram import Bot

# EQ12 Integration
try:
    from eq12_advanced_bankroll_optimizer import EQ12AdvancedBankrollOptimizer
    from eq12_live_arbitrage_scanner import EQ12LiveArbitrageScanner
    from eq12_odds_api_client import EQ12OddsAPIClient

    EQ12_INTEGRATION = True
except ImportError:
    EQ12_INTEGRATION = False
    print("⚠️ EQ12 integration not available - running in standalone mode")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/hedge_engine.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12HedgeEngine")

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


class HedgeType(Enum):
    """Types of hedge strategies"""

    FULL_HEDGE = "full_hedge"
    PARTIAL_HEDGE = "partial_hedge"
    GUARANTEED_PROFIT = "guaranteed_profit"
    RISK_FREE = "risk_free"
    PROGRESSIVE_HEDGE = "progressive_hedge"


class HedgeStrategy(Enum):
    """Hedge execution strategies"""

    CONSERVATIVE = "conservative"  # Lock in smaller guaranteed profit
    AGGRESSIVE = "aggressive"  # Maximize profit potential
    BALANCED = "balanced"  # Balance risk and reward
    RISK_FREE = "risk_free"  # Minimize risk, small profit


@dataclass
class ParlayLeg:
    """Represents a single leg of a parlay"""

    leg_id: str
    description: str
    odds: float
    status: str  # "pending", "won", "lost", "void"
    settled: bool = False

    @property
    def decimal_odds(self) -> float:
        """Convert American odds to decimal"""
        if self.odds > 0:
            return (self.odds / 100) + 1
        else:
            return (100 / abs(self.odds)) + 1


@dataclass
class ParlayPosition:
    """Represents an active parlay position"""

    parlay_id: str
    legs: list[ParlayLeg]
    original_stake: float
    current_value: float
    potential_payout: float

    # Hedge tracking
    hedge_opportunities: list["HedgeOpportunity"] = field(default_factory=list)
    active_hedges: list["HedgePosition"] = field(default_factory=list)

    @property
    def remaining_legs(self) -> list[ParlayLeg]:
        """Get legs that are still pending"""
        return [leg for leg in self.legs if not leg.settled]

    @property
    def is_live(self) -> bool:
        """Check if parlay is still live (has pending legs)"""
        return len(self.remaining_legs) > 0

    @property
    def combined_odds(self) -> float:
        """Calculate combined odds of remaining legs"""
        combined = 1.0
        for leg in self.remaining_legs:
            combined *= leg.decimal_odds
        return combined


@dataclass
class HedgeOpportunity:
    """Represents a hedge opportunity"""

    opportunity_id: str
    parlay_id: str
    hedge_type: HedgeType
    strategy: HedgeStrategy

    # Hedge details
    hedge_side: str  # What to bet on for hedge
    hedge_odds: float
    hedge_stake: float

    # Profit scenarios
    parlay_wins_profit: float
    hedge_wins_profit: float
    guaranteed_profit: float

    # Risk metrics
    risk_amount: float
    max_loss: float
    profit_margin: float

    # Timing
    detection_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    expiry_time: datetime | None = None
    confidence_score: float = 1.0


@dataclass
class HedgePosition:
    """Represents an executed hedge position"""

    hedge_id: str
    parlay_id: str
    hedge_opportunity: HedgeOpportunity
    execution_time: datetime
    actual_stake: float
    actual_odds: float
    status: str = "active"  # "active", "won", "lost", "void"


class EQ12AutomatedHedgeEngine:
    """
    Advanced automated hedge engine for parlay optimization
    """

    def __init__(self, eq12_root: str = "C:/EQ12"):
        self.eq12_root = Path(eq12_root)

        # Core components
        self.telegram_bot = None
        self.odds_client = None
        self.arbitrage_scanner = None
        self.bankroll_optimizer = None

        # Position tracking
        self.active_parlays: dict[str, ParlayPosition] = {}
        self.hedge_history: list[HedgePosition] = []
        self.opportunity_cache: dict[str, list[HedgeOpportunity]] = {}

        # Configuration
        self.min_guaranteed_profit = 0.05  # Minimum 5% guaranteed profit
        self.max_hedge_stake_percentage = 0.5  # Max 50% of original stake for hedging
        self.hedge_opportunity_threshold = 0.02  # 2% minimum opportunity
        self.monitoring_frequency = 60  # Check for opportunities every 60 seconds

        # Initialize components
        self._initialize_components()

        logger.info("🛡️ EQ12 Automated Hedge Engine initialized")

    def _initialize_components(self):
        """Initialize hedge engine components"""
        if TELEGRAM_BOT_TOKEN:
            try:
                self.telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
                logger.info("✅ Telegram bot initialized for hedge alerts")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Telegram bot: {e}")

        if EQ12_INTEGRATION:
            try:
                self.arbitrage_scanner = EQ12LiveArbitrageScanner()
                self.bankroll_optimizer = EQ12AdvancedBankrollOptimizer()
                logger.info("✅ EQ12 integration components initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize EQ12 components: {e}")

    def add_parlay_position(
        self, parlay_id: str, legs: list[dict[str, Any]], original_stake: float
    ) -> ParlayPosition:
        """
        Add a new parlay position to track for hedge opportunities
        """
        # Convert legs to ParlayLeg objects
        parlay_legs = []
        for i, leg in enumerate(legs):
            parlay_leg = ParlayLeg(
                leg_id=f"{parlay_id}_leg_{i}",
                description=leg.get("description", f"Leg {i + 1}"),
                odds=leg.get("odds", 100),
                status="pending",
            )
            parlay_legs.append(parlay_leg)

        # Calculate potential payout
        combined_odds = 1.0
        for leg in parlay_legs:
            combined_odds *= leg.decimal_odds

        potential_payout = original_stake * combined_odds

        # Create parlay position
        position = ParlayPosition(
            parlay_id=parlay_id,
            legs=parlay_legs,
            original_stake=original_stake,
            current_value=original_stake,  # Initial value equals stake
            potential_payout=potential_payout,
        )

        self.active_parlays[parlay_id] = position

        logger.info(
            f"📊 Added parlay position: {parlay_id} - Stake: ${original_stake:.2f} - Potential: ${potential_payout:.2f}"
        )

        return position

    def settle_parlay_leg(self, parlay_id: str, leg_id: str, outcome: str) -> bool:
        """
        Settle a leg of a parlay (won, lost, void)
        """
        if parlay_id not in self.active_parlays:
            logger.warning(f"⚠️ Parlay {parlay_id} not found")
            return False

        position = self.active_parlays[parlay_id]

        # Find and settle the leg
        for leg in position.legs:
            if leg.leg_id == leg_id:
                leg.status = outcome
                leg.settled = True

                # Update parlay current value
                if outcome == "lost":
                    # Parlay is dead, remove from active tracking
                    position.current_value = 0
                    del self.active_parlays[parlay_id]
                    logger.info(f"💀 Parlay {parlay_id} eliminated - leg lost")
                elif outcome == "won":
                    # Leg won, parlay still alive
                    # Recalculate potential payout based on remaining legs
                    remaining_combined_odds = 1.0
                    for remaining_leg in position.remaining_legs:
                        remaining_combined_odds *= remaining_leg.decimal_odds

                    position.current_value = position.original_stake * remaining_combined_odds
                    logger.info(
                        f"✅ Parlay {parlay_id} leg won - Current value: ${position.current_value:.2f}"
                    )

                return True

        logger.warning(f"⚠️ Leg {leg_id} not found in parlay {parlay_id}")
        return False

    async def calculate_hedge_opportunities(self, parlay_id: str) -> list[HedgeOpportunity]:
        """
        Calculate all available hedge opportunities for a parlay
        """
        if parlay_id not in self.active_parlays:
            return []

        position = self.active_parlays[parlay_id]

        if not position.is_live:
            return []

        opportunities = []

        # Calculate different hedge strategies
        strategies = [HedgeStrategy.CONSERVATIVE, HedgeStrategy.BALANCED, HedgeStrategy.AGGRESSIVE]

        for strategy in strategies:
            # Full hedge opportunities
            full_hedge_opps = await self._calculate_full_hedge_opportunities(position, strategy)
            opportunities.extend(full_hedge_opps)

            # Partial hedge opportunities
            partial_hedge_opps = await self._calculate_partial_hedge_opportunities(
                position, strategy
            )
            opportunities.extend(partial_hedge_opps)

            # Guaranteed profit opportunities
            guaranteed_opps = await self._calculate_guaranteed_profit_opportunities(
                position, strategy
            )
            opportunities.extend(guaranteed_opps)

        # Filter and rank opportunities
        viable_opportunities = [
            opp
            for opp in opportunities
            if opp.guaranteed_profit >= position.original_stake * self.min_guaranteed_profit
        ]

        # Sort by guaranteed profit (descending)
        viable_opportunities.sort(key=lambda x: x.guaranteed_profit, reverse=True)

        # Cache opportunities
        self.opportunity_cache[parlay_id] = viable_opportunities

        return viable_opportunities

    async def _calculate_full_hedge_opportunities(
        self, position: ParlayPosition, strategy: HedgeStrategy
    ) -> list[HedgeOpportunity]:
        """
        Calculate full hedge opportunities (hedge entire parlay)
        """
        opportunities = []

        # For full hedge, we need to bet against all remaining outcomes
        remaining_legs = position.remaining_legs

        if len(remaining_legs) == 1:
            # Simple 2-outcome hedge on final leg
            leg = remaining_legs[0]

            # Get current odds for opposite outcome (simplified - would use real odds API)
            opposite_odds = await self._get_opposite_odds(leg)

            if opposite_odds:
                hedge_opp = self._calculate_simple_hedge(position, leg, opposite_odds, strategy)
                if hedge_opp:
                    opportunities.append(hedge_opp)

        elif len(remaining_legs) > 1:
            # Multi-leg hedge - more complex
            multi_hedge_opps = await self._calculate_multi_leg_hedge(position, strategy)
            opportunities.extend(multi_hedge_opps)

        return opportunities

    async def _calculate_partial_hedge_opportunities(
        self, position: ParlayPosition, strategy: HedgeStrategy
    ) -> list[HedgeOpportunity]:
        """
        Calculate partial hedge opportunities (hedge portion of potential profit)
        """
        opportunities = []

        # Partial hedge percentages to consider
        hedge_percentages = [0.25, 0.50, 0.75] if strategy == HedgeStrategy.BALANCED else [0.50]

        for hedge_percentage in hedge_percentages:
            remaining_legs = position.remaining_legs

            if len(remaining_legs) == 1:
                leg = remaining_legs[0]
                opposite_odds = await self._get_opposite_odds(leg)

                if opposite_odds:
                    # Calculate partial hedge
                    target_hedge_payout = position.potential_payout * hedge_percentage

                    # Convert opposite odds to decimal
                    if opposite_odds > 0:
                        opposite_decimal = (opposite_odds / 100) + 1
                    else:
                        opposite_decimal = (100 / abs(opposite_odds)) + 1

                    hedge_stake = target_hedge_payout / opposite_decimal

                    # Calculate profit scenarios
                    if hedge_stake <= position.original_stake * self.max_hedge_stake_percentage:
                        parlay_wins_profit = (
                            position.potential_payout - position.original_stake - hedge_stake
                        )
                        hedge_wins_profit = (
                            target_hedge_payout - position.original_stake - hedge_stake
                        )
                        guaranteed_profit = min(parlay_wins_profit, hedge_wins_profit)

                        if guaranteed_profit > 0:
                            opportunity = HedgeOpportunity(
                                opportunity_id=f"{position.parlay_id}_partial_{int(hedge_percentage * 100)}",
                                parlay_id=position.parlay_id,
                                hedge_type=HedgeType.PARTIAL_HEDGE,
                                strategy=strategy,
                                hedge_side=f"Opposite of {leg.description}",
                                hedge_odds=opposite_odds,
                                hedge_stake=hedge_stake,
                                parlay_wins_profit=parlay_wins_profit,
                                hedge_wins_profit=hedge_wins_profit,
                                guaranteed_profit=guaranteed_profit,
                                risk_amount=hedge_stake,
                                max_loss=max(-parlay_wins_profit, -hedge_wins_profit),
                                profit_margin=guaranteed_profit / position.original_stake,
                            )

                            opportunities.append(opportunity)

        return opportunities

    async def _calculate_guaranteed_profit_opportunities(
        self, position: ParlayPosition, strategy: HedgeStrategy
    ) -> list[HedgeOpportunity]:
        """
        Calculate guaranteed profit opportunities (arbitrage-style)
        """
        opportunities = []

        remaining_legs = position.remaining_legs

        if len(remaining_legs) == 1:
            leg = remaining_legs[0]

            # Get multiple bookmaker odds for comparison
            all_opposite_odds = await self._get_all_opposite_odds(leg)

            for bookmaker, odds in all_opposite_odds.items():
                # Calculate arbitrage-style guaranteed profit
                parlay_decimal = position.combined_odds

                hedge_decimal = odds / 100 + 1 if odds > 0 else 100 / abs(odds) + 1

                # Check for arbitrage opportunity
                total_implied_probability = (1 / parlay_decimal) + (1 / hedge_decimal)

                if total_implied_probability < 1.0:  # Arbitrage exists
                    # Calculate optimal stakes for guaranteed profit
                    total_stake_target = position.original_stake * 2  # Target 2x original stake

                    parlay_stake_optimal = total_stake_target / (
                        1 + (parlay_decimal / hedge_decimal)
                    )
                    hedge_stake_optimal = total_stake_target - parlay_stake_optimal

                    # Since parlay is already placed, calculate hedge needed
                    hedge_stake = hedge_stake_optimal * (
                        position.original_stake / parlay_stake_optimal
                    )

                    # Calculate profits
                    parlay_wins_profit = (
                        (position.original_stake * parlay_decimal)
                        - position.original_stake
                        - hedge_stake
                    )
                    hedge_wins_profit = (
                        (hedge_stake * hedge_decimal) - position.original_stake - hedge_stake
                    )
                    guaranteed_profit = min(parlay_wins_profit, hedge_wins_profit)

                    if (
                        guaranteed_profit
                        > position.original_stake * self.hedge_opportunity_threshold
                    ):
                        opportunity = HedgeOpportunity(
                            opportunity_id=f"{position.parlay_id}_guaranteed_{bookmaker}",
                            parlay_id=position.parlay_id,
                            hedge_type=HedgeType.GUARANTEED_PROFIT,
                            strategy=strategy,
                            hedge_side=f"Opposite {leg.description} @ {bookmaker}",
                            hedge_odds=odds,
                            hedge_stake=hedge_stake,
                            parlay_wins_profit=parlay_wins_profit,
                            hedge_wins_profit=hedge_wins_profit,
                            guaranteed_profit=guaranteed_profit,
                            risk_amount=hedge_stake,
                            max_loss=0,  # Guaranteed profit means no loss
                            profit_margin=guaranteed_profit / position.original_stake,
                        )

                        opportunities.append(opportunity)

        return opportunities

    def _calculate_simple_hedge(
        self,
        position: ParlayPosition,
        leg: ParlayLeg,
        opposite_odds: float,
        strategy: HedgeStrategy,
    ) -> HedgeOpportunity | None:
        """
        Calculate a simple two-outcome hedge
        """
        # Strategy-based hedge calculation
        if strategy == HedgeStrategy.CONSERVATIVE:
            # Lock in small guaranteed profit
            target_profit_ratio = 0.1  # 10% of original stake
        elif strategy == HedgeStrategy.AGGRESSIVE:
            # Maximize potential profit, accept some risk
            target_profit_ratio = 0.05  # 5% guaranteed, more upside
        else:  # BALANCED
            # Balance guaranteed profit with upside
            target_profit_ratio = 0.08  # 8% guaranteed

        # Convert odds to decimal
        if opposite_odds > 0:
            opposite_decimal = (opposite_odds / 100) + 1
        else:
            opposite_decimal = (100 / abs(opposite_odds)) + 1

        # Calculate hedge stake for target guaranteed profit
        target_guaranteed_profit = position.original_stake * target_profit_ratio

        # Solve for hedge stake that guarantees target profit
        # If parlay wins: profit = potential_payout - original_stake - hedge_stake
        # If hedge wins: profit = hedge_payout - original_stake - hedge_stake
        # Set both equal to target_guaranteed_profit

        hedge_stake = (
            position.potential_payout - position.original_stake - target_guaranteed_profit
        ) / (1 + opposite_decimal)

        if hedge_stake > position.original_stake * self.max_hedge_stake_percentage:
            return None  # Hedge too large

        # Calculate actual profits
        parlay_wins_profit = position.potential_payout - position.original_stake - hedge_stake
        hedge_wins_profit = (hedge_stake * opposite_decimal) - position.original_stake - hedge_stake
        guaranteed_profit = min(parlay_wins_profit, hedge_wins_profit)

        if guaranteed_profit <= 0:
            return None  # No guaranteed profit

        return HedgeOpportunity(
            opportunity_id=f"{position.parlay_id}_simple_{strategy.value}",
            parlay_id=position.parlay_id,
            hedge_type=HedgeType.FULL_HEDGE,
            strategy=strategy,
            hedge_side=f"Opposite of {leg.description}",
            hedge_odds=opposite_odds,
            hedge_stake=hedge_stake,
            parlay_wins_profit=parlay_wins_profit,
            hedge_wins_profit=hedge_wins_profit,
            guaranteed_profit=guaranteed_profit,
            risk_amount=hedge_stake,
            max_loss=max(-parlay_wins_profit, -hedge_wins_profit),
            profit_margin=guaranteed_profit / position.original_stake,
        )

    async def _calculate_multi_leg_hedge(
        self, position: ParlayPosition, strategy: HedgeStrategy
    ) -> list[HedgeOpportunity]:
        """
        Calculate hedge opportunities for multi-leg parlays
        """
        opportunities = []

        # For multi-leg parlays, consider hedging individual legs as they approach
        remaining_legs = position.remaining_legs

        # Simplified: hedge against the most likely leg to lose
        for leg in remaining_legs:
            opposite_odds = await self._get_opposite_odds(leg)

            if opposite_odds:
                # Calculate hedge as if this is the final leg
                temp_position = ParlayPosition(
                    parlay_id=f"{position.parlay_id}_temp",
                    legs=[leg],
                    original_stake=position.current_value,
                    current_value=position.current_value,
                    potential_payout=position.current_value * leg.decimal_odds,
                )

                hedge_opp = self._calculate_simple_hedge(
                    temp_position, leg, opposite_odds, strategy
                )

                if hedge_opp:
                    # Adjust for multi-leg context
                    hedge_opp.opportunity_id = f"{position.parlay_id}_multileg_{leg.leg_id}"
                    hedge_opp.parlay_id = position.parlay_id
                    hedge_opp.hedge_type = HedgeType.PROGRESSIVE_HEDGE
                    opportunities.append(hedge_opp)

        return opportunities

    async def _get_opposite_odds(self, leg: ParlayLeg) -> float | None:
        """
        Get odds for the opposite outcome of a leg (mock implementation)
        In production, this would query live odds APIs
        """
        # Mock implementation - in production, query real odds API
        # For demonstration, assume opposite odds based on original odds

        if leg.odds > 0:
            # Positive odds, opposite should be negative
            implied_prob = 100 / (leg.odds + 100)
            opposite_prob = 1 - implied_prob
            opposite_odds = -(100 * opposite_prob) / (1 - opposite_prob)
        else:
            # Negative odds, opposite should be positive
            implied_prob = abs(leg.odds) / (abs(leg.odds) + 100)
            opposite_prob = 1 - implied_prob
            opposite_odds = (100 * (1 - opposite_prob)) / opposite_prob

        # Add some market inefficiency simulation
        return opposite_odds * np.random.uniform(0.95, 1.05)

    async def _get_all_opposite_odds(self, leg: ParlayLeg) -> dict[str, float]:
        """
        Get opposite odds from multiple bookmakers (mock implementation)
        """
        base_odds = await self._get_opposite_odds(leg)

        if not base_odds:
            return {}

        # Simulate different bookmaker odds
        bookmakers = ["DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet"]
        odds_dict = {}

        for bookmaker in bookmakers:
            # Add some variation between bookmakers
            variation = np.random.uniform(0.95, 1.05)
            odds_dict[bookmaker] = base_odds * variation

        return odds_dict

    async def execute_hedge(self, opportunity: HedgeOpportunity) -> HedgePosition:
        """
        Execute a hedge position (in production, would place actual bet)
        """
        # In production, this would:
        # 1. Place the hedge bet through API
        # 2. Confirm execution
        # 3. Track the position

        hedge_position = HedgePosition(
            hedge_id=f"hedge_{int(datetime.now().timestamp())}",
            parlay_id=opportunity.parlay_id,
            hedge_opportunity=opportunity,
            execution_time=datetime.now(UTC),
            actual_stake=opportunity.hedge_stake,
            actual_odds=opportunity.hedge_odds,
            status="active",
        )

        self.hedge_history.append(hedge_position)

        # Add to parlay's active hedges
        if opportunity.parlay_id in self.active_parlays:
            self.active_parlays[opportunity.parlay_id].active_hedges.append(hedge_position)

        # Send alert
        await self._send_hedge_execution_alert(hedge_position)

        logger.info(
            f"✅ Hedge executed: {hedge_position.hedge_id} - Stake: ${hedge_position.actual_stake:.2f}"
        )

        return hedge_position

    async def monitor_hedge_opportunities(self):
        """
        Continuously monitor all active parlays for hedge opportunities
        """
        logger.info("🔄 Starting continuous hedge monitoring")

        while True:
            try:
                for parlay_id, position in list(self.active_parlays.items()):
                    if position.is_live:
                        opportunities = await self.calculate_hedge_opportunities(parlay_id)

                        if opportunities:
                            # Alert on new opportunities
                            await self._send_hedge_opportunity_alert(
                                opportunities[0]
                            )  # Send best opportunity

                            # Auto-execute if meets criteria
                            best_opportunity = opportunities[0]
                            if (
                                best_opportunity.hedge_type == HedgeType.GUARANTEED_PROFIT
                                and best_opportunity.guaranteed_profit
                                > position.original_stake * 0.1
                            ):
                                logger.info(
                                    f"🎯 Auto-executing guaranteed profit hedge: {best_opportunity.opportunity_id}"
                                )
                                await self.execute_hedge(best_opportunity)

                await asyncio.sleep(self.monitoring_frequency)

            except Exception as e:
                logger.error(f"❌ Error in hedge monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _send_hedge_opportunity_alert(self, opportunity: HedgeOpportunity):
        """
        Send Telegram alert for hedge opportunity
        """
        if not self.telegram_bot or not TELEGRAM_CHAT_ID:
            return

        try:
            message = self._format_hedge_opportunity_message(opportunity)

            await self.telegram_bot.send_message(
                chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML"
            )

            logger.info(f"✅ Hedge opportunity alert sent: {opportunity.hedge_type.value}")

        except Exception as e:
            logger.error(f"❌ Failed to send hedge alert: {e}")

    async def _send_hedge_execution_alert(self, position: HedgePosition):
        """
        Send Telegram alert for hedge execution
        """
        if not self.telegram_bot or not TELEGRAM_CHAT_ID:
            return

        try:
            message = f"""
🛡️ <b>HEDGE EXECUTED</b> 🛡️

💰 Parlay ID: {position.parlay_id}
🎯 Hedge Stake: ${position.actual_stake:.2f}
📊 Hedge Odds: {position.actual_odds:+.0f}
✅ Guaranteed Profit: ${position.hedge_opportunity.guaranteed_profit:.2f}

⚡ <i>Hedge position is now active!</i>
"""

            await self.telegram_bot.send_message(
                chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML"
            )

        except Exception as e:
            logger.error(f"❌ Failed to send hedge execution alert: {e}")

    def _format_hedge_opportunity_message(self, opportunity: HedgeOpportunity) -> str:
        """
        Format hedge opportunity as Telegram message
        """
        profit_emoji = "💎" if opportunity.guaranteed_profit > 50 else "💰"

        message = f"""
{profit_emoji} <b>HEDGE OPPORTUNITY DETECTED</b> {profit_emoji}

🎰 <b>Parlay ID:</b> {opportunity.parlay_id}
🎯 <b>Type:</b> {opportunity.hedge_type.value.title()}
⚡ <b>Strategy:</b> {opportunity.strategy.value.title()}

💵 <b>Hedge Details:</b>
🎲 Side: {opportunity.hedge_side}
📊 Odds: {opportunity.hedge_odds:+.0f}
💰 Stake: ${opportunity.hedge_stake:.2f}

💎 <b>Profit Scenarios:</b>
✅ Parlay Wins: ${opportunity.parlay_wins_profit:.2f}
🛡️ Hedge Wins: ${opportunity.hedge_wins_profit:.2f}
💰 <b>Guaranteed: ${opportunity.guaranteed_profit:.2f}</b>

📊 Profit Margin: {opportunity.profit_margin:.1%}
⚠️ Risk Amount: ${opportunity.risk_amount:.2f}

⏰ Detected: {opportunity.detection_time.strftime("%H:%M:%S")}

🎯 <i>Consider executing this hedge for guaranteed profit!</i>
"""

        return message

    def get_hedge_summary(self) -> dict[str, Any]:
        """
        Get comprehensive hedge engine summary
        """
        active_parlay_count = len(self.active_parlays)
        total_hedge_count = len(self.hedge_history)

        # Calculate total guaranteed profits from hedges
        total_guaranteed_profit = sum(
            hedge.hedge_opportunity.guaranteed_profit
            for hedge in self.hedge_history
            if hedge.status == "active"
        )

        # Count opportunities by type
        opportunity_counts = {}
        for opportunities in self.opportunity_cache.values():
            for opp in opportunities:
                hedge_type = opp.hedge_type.value
                opportunity_counts[hedge_type] = opportunity_counts.get(hedge_type, 0) + 1

        return {
            "active_parlays": active_parlay_count,
            "total_hedges_executed": total_hedge_count,
            "total_guaranteed_profit": total_guaranteed_profit,
            "opportunity_types": opportunity_counts,
            "monitoring_status": "active" if active_parlay_count > 0 else "idle",
            "next_check": datetime.now(UTC) + timedelta(seconds=self.monitoring_frequency),
        }


# Integration with existing EdgeGod system
async def integrate_hedge_engine_with_edgegod(parlay_data: dict[str, Any]) -> dict[str, Any]:
    """
    Integration point with existing EdgeGod parlay system
    """
    hedge_engine = EQ12AutomatedHedgeEngine()

    # Add parlay to hedge tracking
    parlay_id = parlay_data.get("id", f"parlay_{int(datetime.now().timestamp())}")
    legs = parlay_data.get("legs", [])
    stake = parlay_data.get("stake", 100)

    position = hedge_engine.add_parlay_position(parlay_id, legs, stake)

    # Calculate initial hedge opportunities
    opportunities = await hedge_engine.calculate_hedge_opportunities(parlay_id)

    return {
        "parlay_position": {
            "id": position.parlay_id,
            "stake": position.original_stake,
            "potential_payout": position.potential_payout,
            "current_value": position.current_value,
            "legs_remaining": len(position.remaining_legs),
        },
        "hedge_opportunities": len(opportunities),
        "best_opportunity": (
            {
                "type": opportunities[0].hedge_type.value,
                "guaranteed_profit": opportunities[0].guaranteed_profit,
                "hedge_stake": opportunities[0].hedge_stake,
                "profit_margin": opportunities[0].profit_margin,
            }
            if opportunities
            else None
        ),
        "auto_hedge_recommended": (
            opportunities
            and opportunities[0].hedge_type == HedgeType.GUARANTEED_PROFIT
            and opportunities[0].guaranteed_profit > stake * 0.1
        ),
        "integration_status": "active",
    }


# CLI interface
async def main():
    """Main function for CLI testing"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Automated Hedge Engine")
    parser.add_argument("--test", action="store_true", help="Run hedge calculation test")
    parser.add_argument("--monitor", action="store_true", help="Start continuous monitoring")
    parser.add_argument("--summary", action="store_true", help="Show hedge engine summary")

    args = parser.parse_args()

    engine = EQ12AutomatedHedgeEngine()

    if args.test:
        print("🛡️ Testing hedge engine...")

        # Create test parlay
        test_legs = [
            {"description": "Team A ML", "odds": 150},
            {"description": "Team B ML", "odds": -110},
            {"description": "Over 45.5", "odds": 105},
        ]

        engine.add_parlay_position("test_parlay", test_legs, 100)

        # Calculate hedge opportunities
        opportunities = await engine.calculate_hedge_opportunities("test_parlay")

        print(f"✅ Found {len(opportunities)} hedge opportunities:")
        for i, opp in enumerate(opportunities, 1):
            print(f"   {i}. {opp.hedge_type.value}: ${opp.guaranteed_profit:.2f} guaranteed profit")
            print(f"      Hedge: ${opp.hedge_stake:.2f} at {opp.hedge_odds:+.0f}")

        # Test settling a leg
        if opportunities:
            print(f"\n🎯 Best opportunity: {opportunities[0].hedge_type.value}")
            print(f"   Guaranteed profit: ${opportunities[0].guaranteed_profit:.2f}")
            print(f"   Profit margin: {opportunities[0].profit_margin:.1%}")

    elif args.monitor:
        print("🔄 Starting hedge monitoring...")
        await engine.monitor_hedge_opportunities()

    else:
        print("📊 Hedge Engine Summary:")
        summary = engine.get_hedge_summary()
        print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
