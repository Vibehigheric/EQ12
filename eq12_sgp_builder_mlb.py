#!/usr/bin/env python3
"""
EQ12 MLB Playoffs SGP Generator
==============================
DraftKings SGP builder with playoff-optimized templates:
- Ace Domination: SP Ks Over + Opp Team Total Under + Opp Hits Under
- Power Stack: Slugger TB Over + Slugger HR + Team Total Over + Opp SP Outs Under
- Small-Ball Stack: Leadoff TB/H+R+RBI Over + Team Total Over
- Unders Script: Both SP Outs Over + Game Total Under + Key Batter TB Under

Max 3-4 legs, correlation penalties, guardrails for sharp playoff pricing
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime


@dataclass
class SGPLeg:
    leg_type: str  # pitcher_k_over, team_total_over, batter_tb_over, etc.
    player_name: str | None
    team: str
    line: float
    odds: int  # American odds
    selection: str  # over/under/yes/no
    description: str
    correlation_penalty: float  # Applied adjustment


@dataclass
class PlayoffSGP:
    template_name: str
    game_matchup: str
    legs: list[SGPLeg]
    raw_odds: int  # Before correlation adjustments
    adjusted_odds: int  # After correlation penalties
    payout_multiplier: float
    confidence: int  # 1-10
    max_bet_pct: float  # % of bankroll (0.5-1.5% for playoffs)
    risk_factors: list[str]
    build_instructions: str  # How to build on DraftKings


class MLBPlayoffSGPGenerator:
    """Generate playoff-optimized SGPs with correlation adjustments"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        # Load SGP templates
        self.templates = self._load_sgp_templates()

        # Playoff-specific constraints
        self.max_legs = 4  # Tighter than regular season (5-6)
        self.max_daily_sgps = 5  # Limit exposure
        self.max_bet_pct = 1.5  # Max 1.5% bankroll per SGP

        # Correlation penalties (playoff markets are sharper)
        self.correlation_matrix = {
            # Pitcher ↔ Opposing batters (negative correlation)
            ("pitcher_k_over", "opp_team_total_over"): -0.05,
            ("pitcher_k_over", "opp_batter_tb_over"): -0.04,
            ("pitcher_outs_over", "opp_team_total_over"): -0.08,
            # Team offense ↔ Opposing pitcher (negative correlation)
            ("team_total_over", "opp_pitcher_k_over"): -0.03,
            ("batter_tb_over", "opp_pitcher_outs_over"): -0.06,
            # Within-team synergies (small positive correlation)
            ("team_total_over", "batter_tb_over"): +0.01,
            ("batter_tb_over", "batter_hr"): +0.02,
            # Weather/conditions
            ("wind_in_10mph", "hr_under"): +0.03,
            ("dome_game", "total_consistency"): +0.01,
        }

    def setup_logging(self):
        """Setup playoff SGP logging"""
        log_dir = r"C:\EQ12\logs"
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f"playoff_sgp_{datetime.now().strftime('%Y%m%d')}.log")

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

    def _load_sgp_templates(self) -> dict[str, dict]:
        """Load SGP template configurations"""

        # Embedded templates (in production, load from YAML file)
        templates = {
            "ace_domination": {
                "description": "SP Ks Over + Opp Team Total Under + Opp Hits Under",
                "legs": [
                    {"type": "pitcher_k_over", "required": True},
                    {"type": "opp_team_total_under", "required": True},
                    {"type": "opp_hits_under", "required": False},
                ],
                "max_legs": 3,
                "correlation_penalties": {
                    "opp_team_total_under": -0.03,
                    "opp_hits_under": -0.02,
                },
                "confidence_base": 7,
                "playoff_adjustment": -0.05,  # Sharper pricing in playoffs
            },
            "power_stack": {
                "description": "Slugger TB Over + HR + Team Total Over + Opp SP Outs Under",
                "legs": [
                    {"type": "batter_tb_over", "required": True},
                    {"type": "batter_hr", "required": False},
                    {"type": "team_total_over", "required": True},
                    {"type": "opp_sp_outs_under", "required": False},
                ],
                "max_legs": 4,
                "correlation_penalties": {
                    "team_total_over": 0.00,  # Positive correlation within team
                    "batter_hr": +0.01,
                    "opp_sp_outs_under": -0.04,
                },
                "confidence_base": 6,
                "playoff_adjustment": -0.08,
            },
            "small_ball_stack": {
                "description": "Leadoff H+R+RBI Over + Team Total Over + Speed elements",
                "legs": [
                    {"type": "leadoff_hrbi_over", "required": True},
                    {"type": "team_total_over", "required": True},
                    {"type": "team_hits_over", "required": False},
                ],
                "max_legs": 3,
                "correlation_penalties": {
                    "team_total_over": +0.01,  # Synergy
                    "team_hits_over": +0.01,
                },
                "confidence_base": 6,
                "playoff_adjustment": -0.03,
            },
            "unders_script": {
                "description": "Both SP Outs Over + Game Total Under + Key Batter TB Under",
                "legs": [
                    {"type": "home_sp_outs_over", "required": True},
                    {"type": "away_sp_outs_over", "required": True},
                    {"type": "game_total_under", "required": True},
                    {"type": "key_batter_tb_under", "required": False},
                ],
                "max_legs": 4,
                "correlation_penalties": {
                    "game_total_under": -0.02,  # Moderate correlation
                    "key_batter_tb_under": -0.01,
                },
                "confidence_base": 8,  # Pitchers duels more predictable
                "playoff_adjustment": 0.00,  # Unders hold value better
            },
        }

        return templates

    def generate_sgp_from_template(
        self, template_name: str, game_data: dict, player_props: dict
    ) -> PlayoffSGP | None:
        """Generate SGP using specific template"""

        if template_name not in self.templates:
            self.logger.error(f"Template {template_name} not found")
            return None

        template = self.templates[template_name]
        self.logger.info(f"🎲 Building {template_name} SGP for {game_data.get('matchup', 'TBD')}")

        legs = []

        # Build legs according to template
        for leg_config in template["legs"]:
            leg = self._build_leg_from_config(leg_config, game_data, player_props)

            if leg:
                legs.append(leg)
            elif leg_config.get("required", False):
                self.logger.warning(f"Required leg {leg_config['type']} missing - skipping SGP")
                return None

        # Enforce max legs for playoffs
        if len(legs) > template.get("max_legs", self.max_legs):
            legs = legs[: template.get("max_legs", self.max_legs)]
            self.logger.info(f"Trimmed to {len(legs)} legs for playoff constraints")

        if len(legs) < 2:
            self.logger.warning("Not enough legs built - skipping SGP")
            return None

        # Calculate raw odds
        raw_odds = self._calculate_raw_odds(legs)

        # Apply correlation penalties
        correlation_penalty = self._calculate_correlation_penalty(legs, template)
        adjusted_odds = self._apply_penalty_to_odds(raw_odds, correlation_penalty)

        # Apply playoff adjustment
        playoff_penalty = template.get("playoff_adjustment", 0.0)
        final_odds = self._apply_penalty_to_odds(adjusted_odds, playoff_penalty)

        # Calculate confidence and risk
        confidence = self._calculate_confidence(template, legs, game_data)
        max_bet_pct = min(self.max_bet_pct, confidence * 0.15)  # Scale with confidence

        # Risk factors
        risk_factors = self._identify_risk_factors(legs, game_data)

        # Build instructions for DraftKings
        build_instructions = self._generate_build_instructions(legs)

        playoff_sgp = PlayoffSGP(
            template_name=template_name,
            game_matchup=game_data.get("matchup", "TBD"),
            legs=legs,
            raw_odds=raw_odds,
            adjusted_odds=final_odds,
            payout_multiplier=self._odds_to_decimal(final_odds),
            confidence=confidence,
            max_bet_pct=max_bet_pct,
            risk_factors=risk_factors,
            build_instructions=build_instructions,
        )

        self.logger.info(
            f"✅ Built {template_name}: {final_odds:+d} odds, {confidence}/10 confidence"
        )

        return playoff_sgp

    def _build_leg_from_config(
        self, leg_config: dict, game_data: dict, player_props: dict
    ) -> SGPLeg | None:
        """Build individual SGP leg from configuration"""

        leg_type = leg_config["type"]

        # Route to specific builders based on leg type
        if leg_type == "pitcher_k_over":
            return self._build_pitcher_k_leg(game_data, player_props, "home")
        if leg_type == "opp_team_total_under":
            return self._build_team_total_leg(game_data, "away", "under")
        if leg_type == "batter_tb_over":
            return self._build_batter_tb_leg(game_data, player_props, "home")
        if leg_type == "team_total_over":
            return self._build_team_total_leg(game_data, "home", "over")
        if leg_type == "game_total_under":
            return self._build_game_total_leg(game_data, "under")
        # Add more leg builders as needed
        self.logger.warning(f"Unknown leg type: {leg_type}")
        return None

    def _build_pitcher_k_leg(
        self, game_data: dict, player_props: dict, team_side: str
    ) -> SGPLeg | None:
        """Build pitcher strikeouts over leg"""

        pitcher_key = f"{team_side}_pitcher"
        pitcher_name = game_data.get(pitcher_key, {}).get("name")

        if not pitcher_name:
            return None

        # Get strikeout line (from props or estimate)
        k_line = player_props.get(pitcher_name, {}).get("strikeouts", 5.5)
        k_odds = -115  # Typical playoff K over odds

        return SGPLeg(
            leg_type="pitcher_k_over",
            player_name=pitcher_name,
            team=game_data.get(f"{team_side}_team", ""),
            line=k_line,
            odds=k_odds,
            selection="over",
            description=f"{pitcher_name} Over {k_line} Strikeouts",
            correlation_penalty=0.0,
        )

    def _build_team_total_leg(
        self, game_data: dict, team_side: str, selection: str
    ) -> SGPLeg | None:
        """Build team total over/under leg"""

        team_name = game_data.get(f"{team_side}_team", "")
        team_total_line = game_data.get(f"{team_side}_team_total", 4.5)

        odds = -110 if selection == "over" else -110

        return SGPLeg(
            leg_type=f"team_total_{selection}",
            player_name=None,
            team=team_name,
            line=team_total_line,
            odds=odds,
            selection=selection,
            description=f"{team_name} Team Total {selection.title()} {team_total_line}",
            correlation_penalty=0.0,
        )

    def _build_batter_tb_leg(
        self, game_data: dict, player_props: dict, team_side: str
    ) -> SGPLeg | None:
        """Build batter total bases over leg"""

        # Get top batter for team (simplified)
        batters = game_data.get(f"{team_side}_lineup", [])
        if not batters:
            return None

        top_batter = batters[0] if batters else {"name": "Unknown", "tb_line": 1.5}
        batter_name = top_batter.get("name", "")
        tb_line = top_batter.get("tb_line", 1.5)

        return SGPLeg(
            leg_type="batter_tb_over",
            player_name=batter_name,
            team=game_data.get(f"{team_side}_team", ""),
            line=tb_line,
            odds=-120,
            selection="over",
            description=f"{batter_name} Over {tb_line} Total Bases",
            correlation_penalty=0.0,
        )

    def _build_game_total_leg(self, game_data: dict, selection: str) -> SGPLeg | None:
        """Build game total over/under leg"""

        game_total_line = game_data.get("game_total", 8.5)

        return SGPLeg(
            leg_type=f"game_total_{selection}",
            player_name=None,
            team="Both Teams",
            line=game_total_line,
            odds=-110,
            selection=selection,
            description=f"Game Total {selection.title()} {game_total_line}",
            correlation_penalty=0.0,
        )

    def _calculate_raw_odds(self, legs: list[SGPLeg]) -> int:
        """Calculate raw parlay odds before correlation adjustments"""

        decimal_odds = 1.0
        for leg in legs:
            decimal_odds *= self._odds_to_decimal(leg.odds)

        # Convert back to American
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        return int(-100 / (decimal_odds - 1))

    def _calculate_correlation_penalty(self, legs: list[SGPLeg], template: dict) -> float:
        """Calculate total correlation penalty for leg combination"""

        total_penalty = 0.0

        # Template-specific penalties
        template_penalties = template.get("correlation_penalties", {})
        for leg in legs:
            penalty = template_penalties.get(leg.leg_type, 0.0)
            total_penalty += penalty

        # Cross-leg correlations from matrix
        for i, leg1 in enumerate(legs):
            for leg2 in legs[i + 1 :]:
                correlation_key = tuple(sorted([leg1.leg_type, leg2.leg_type]))
                penalty = self.correlation_matrix.get(correlation_key, 0.0)
                total_penalty += penalty

        return total_penalty

    def _apply_penalty_to_odds(self, american_odds: int, penalty: float) -> int:
        """Apply correlation penalty to American odds"""

        decimal = self._odds_to_decimal(american_odds)
        adjusted_decimal = decimal * (1 + penalty)  # penalty can be + or -

        # Convert back to American
        if adjusted_decimal >= 2.0:
            return int((adjusted_decimal - 1) * 100)
        return int(-100 / (adjusted_decimal - 1))

    def _odds_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal"""
        if american_odds >= 100:
            return (american_odds / 100) + 1
        return (100 / abs(american_odds)) + 1

    def _calculate_confidence(self, template: dict, legs: list[SGPLeg], game_data: dict) -> int:
        """Calculate confidence score 1-10"""

        base_confidence = template.get("confidence_base", 5)

        # Adjust for game factors
        adjustments = 0

        # Weather factors
        if game_data.get("dome_game", False):
            adjustments += 1  # More predictable conditions

        # Starter quality
        if game_data.get("ace_matchup", False):
            adjustments += 1  # Pitcher props more reliable

        # Playoff context
        if game_data.get("elimination_game", False):
            adjustments -= 1  # Higher variance

        final_confidence = base_confidence + adjustments
        return max(1, min(10, final_confidence))

    def _identify_risk_factors(self, legs: list[SGPLeg], game_data: dict) -> list[str]:
        """Identify risk factors for the SGP"""

        risks = []

        # Weather risks
        if game_data.get("wind_speed", 0) >= 12:
            risks.append(f"High wind {game_data['wind_speed']} mph")

        if game_data.get("rain_chance", 0) >= 30:
            risks.append(f"Rain risk {game_data['rain_chance']}%")

        # Bullpen risks
        bullpen_score = game_data.get("bullpen_readiness", 65)
        if bullpen_score <= 40:
            risks.append("Exhausted bullpen - late inning volatility")

        # Leg-specific risks
        pitcher_legs = [leg for leg in legs if "pitcher" in leg.leg_type]
        if len(pitcher_legs) >= 2:
            risks.append("Multiple pitcher props - starter scratch risk")

        return risks

    def _generate_build_instructions(self, legs: list[SGPLeg]) -> str:
        """Generate DraftKings build instructions"""

        instructions = ["DraftKings SGP Builder Instructions:", ""]

        for i, leg in enumerate(legs, 1):
            instructions.append(f"{i}. Navigate to {leg.description}")
            instructions.append(f"   Select: {leg.selection.upper()}")
            instructions.append("")

        instructions.extend(
            [
                "⚠️ Verify all legs are available before placing bet",
                "⚠️ Check for late scratches before first pitch",
                (
                    f"💰 Max bet: {legs[0].correlation_penalty:.1f}% of bankroll"
                    if legs
                    else "💰 Max bet: 1.0% of bankroll"
                ),
            ]
        )

        return "\n".join(instructions)

    def generate_all_playoff_sgps(
        self, games_data: list[dict], player_props: dict
    ) -> list[PlayoffSGP]:
        """Generate SGPs for all playoff games using all templates"""

        all_sgps = []

        for game_data in games_data:
            self.logger.info(f"🏆 Processing playoff game: {game_data.get('matchup', 'TBD')}")

            # Try each template
            for template_name in self.templates:
                sgp = self.generate_sgp_from_template(template_name, game_data, player_props)

                if sgp:
                    all_sgps.append(sgp)

        # Sort by confidence then odds
        all_sgps.sort(key=lambda x: (x.confidence, x.adjusted_odds), reverse=True)

        # Limit to max daily SGPs
        if len(all_sgps) > self.max_daily_sgps:
            all_sgps = all_sgps[: self.max_daily_sgps]
            self.logger.info(f"Limited to top {self.max_daily_sgps} SGPs for bankroll protection")

        return all_sgps

    def export_sgp_slate(self, sgps: list[PlayoffSGP], output_path: str | None = None) -> str:
        """Export SGP slate to file"""

        if output_path is None:
            log_dir = r"C:\EQ12\logs"
            output_path = os.path.join(
                log_dir,
                f"playoff_sgp_slate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            )

        export_data = {
            "generation_time": datetime.now(UTC).isoformat(),
            "playoff_sgps": len(sgps),
            "total_max_bet_pct": sum(sgp.max_bet_pct for sgp in sgps),
            "sgp_slate": [asdict(sgp) for sgp in sgps],
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"📁 Playoff SGP slate exported to {output_path}")
        return output_path


# Example usage
async def main():
    """Demo playoff SGP generation"""
    generator = MLBPlayoffSGPGenerator()

    print("🏆 MLB Playoff SGP Generator")
    print("=" * 40)

    # Mock playoff game data
    playoff_games = [
        {
            "matchup": "Dodgers @ Braves",
            "home_team": "Atlanta Braves",
            "away_team": "Los Angeles Dodgers",
            "home_pitcher": {"name": "Max Fried"},
            "away_pitcher": {"name": "Walker Buehler"},
            "game_total": 8.0,
            "home_team_total": 4.0,
            "away_team_total": 4.0,
            "ace_matchup": True,
            "dome_game": False,
            "wind_speed": 8,
            "bullpen_readiness": 75,
        }
    ]

    # Mock player props
    player_props = {
        "Max Fried": {"strikeouts": 6.5},
        "Walker Buehler": {"strikeouts": 5.5},
    }

    # Generate SGPs
    sgps = generator.generate_all_playoff_sgps(playoff_games, player_props)

    print(f"\n🎲 Generated {len(sgps)} playoff SGPs:")

    for i, sgp in enumerate(sgps, 1):
        print(f"\n{i}. {sgp.template_name.title()}")
        print(f"   Game: {sgp.game_matchup}")
        print(f"   Odds: {sgp.adjusted_odds:+d} ({sgp.payout_multiplier:.2f}x)")
        print(f"   Confidence: {sgp.confidence}/10")
        print(f"   Max Bet: {sgp.max_bet_pct:.1f}%")
        print(f"   Legs: {len(sgp.legs)}")

        if sgp.risk_factors:
            print(f"   Risks: {', '.join(sgp.risk_factors)}")

    # Export slate
    if sgps:
        output_file = generator.export_sgp_slate(sgps)
        print(f"\n📁 Full slate: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
