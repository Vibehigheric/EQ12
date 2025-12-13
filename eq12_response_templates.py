"""
EQ12 Response Templates - Pre-configured response handlers for specific betting scenarios
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from eq12_model_responses import (
    EQ12ResponsesAPI,
    ResponseConfig,
    ServiceTier,
    ToolType,
)


class BettingScenario(str, Enum):
    """Pre-defined betting scenarios with optimized response templates"""

    NFL_SUNDAY_SLATE = "nfl_sunday_slate"
    NBA_PROPS_NIGHT = "nba_props_night"
    MARCH_MADNESS_BRACKET = "march_madness_bracket"
    PLAYOFF_SERIES_HEDGE = "playoff_series_hedge"
    LIVE_GAME_MOMENTUM = "live_game_momentum"
    WEATHER_IMPACT_TOTALS = "weather_impact_totals"
    INJURY_NEWS_REACTION = "injury_news_reaction"
    SHARP_STEAM_ALERT = "sharp_steam_alert"
    ARBITRAGE_SCANNER = "arbitrage_scanner"
    KELLY_BANKROLL_MANAGER = "kelly_bankroll_manager"


@dataclass
class ScenarioTemplate:
    """Template configuration for betting scenarios"""

    scenario_type: BettingScenario
    instructions: str
    tools: list[ToolType]
    config: ResponseConfig
    output_schema: dict[str, Any]
    metadata_tags: list[str]


class EQ12ResponseTemplates:
    """Pre-configured response templates for common betting scenarios"""

    def __init__(self):
        self.api = EQ12ResponsesAPI()
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> dict[BettingScenario, ScenarioTemplate]:
        """Initialize all response templates"""
        return {
            BettingScenario.NFL_SUNDAY_SLATE: self._nfl_sunday_template(),
            BettingScenario.NBA_PROPS_NIGHT: self._nba_props_template(),
            BettingScenario.MARCH_MADNESS_BRACKET: self._march_madness_template(),
            BettingScenario.PLAYOFF_SERIES_HEDGE: self._playoff_hedge_template(),
            BettingScenario.LIVE_GAME_MOMENTUM: self._live_momentum_template(),
            BettingScenario.WEATHER_IMPACT_TOTALS: self._weather_totals_template(),
            BettingScenario.INJURY_NEWS_REACTION: self._injury_reaction_template(),
            BettingScenario.SHARP_STEAM_ALERT: self._steam_alert_template(),
            BettingScenario.ARBITRAGE_SCANNER: self._arbitrage_template(),
            BettingScenario.KELLY_BANKROLL_MANAGER: self._kelly_manager_template(),
        }

    def _nfl_sunday_template(self) -> ScenarioTemplate:
        """NFL Sunday slate analysis template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.NFL_SUNDAY_SLATE,
            instructions="""You are EQ12 NFL Sunday Expert. Analyze the full slate with focus on:

1. Correlation Mapping: Identify game stack opportunities and negative correlations
2. Weather Impact: Assess wind, temperature, precipitation effects on totals/spreads
3. Injury Updates: Process late-breaking injury news and line movement
4. Public vs Sharp: Distinguish recreational betting patterns from sharp money
5. Divisional Dynamics: Account for rivalry games and historical trends
6. Primetime Adjustments: Factor in national TV game betting patterns
7. Slate Construction: Build optimal DFS + betting portfolio combinations

Focus on high-edge opportunities with proper bankroll allocation across 16+ games.""",
            tools=[ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER, ToolType.FUNCTION],
            config=ResponseConfig(
                model="gpt-4o",
                temperature=0.1,
                max_output_tokens=4000,
                background=True,
                service_tier=ServiceTier.PRIORITY,
            ),
            output_schema={
                "type": "object",
                "properties": {
                    "nfl_slate_analysis": {
                        "type": "object",
                        "properties": {
                            "slate_overview": {
                                "type": "object",
                                "properties": {
                                    "total_games": {"type": "integer"},
                                    "weather_concerns": {"type": "array"},
                                    "key_injuries": {"type": "array"},
                                    "sharp_movement": {"type": "array"},
                                    "public_favorites": {"type": "array"},
                                },
                            },
                            "top_plays": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "game": {"type": "string"},
                                        "play_type": {"type": "string"},
                                        "selection": {"type": "string"},
                                        "confidence": {"type": "string"},
                                        "edge_percentage": {"type": "number"},
                                        "recommended_units": {"type": "number"},
                                        "reasoning": {"type": "string"},
                                    },
                                },
                            },
                            "correlation_stacks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "stack_name": {"type": "string"},
                                        "components": {"type": "array"},
                                        "correlation_strength": {"type": "number"},
                                        "expected_value": {"type": "number"},
                                    },
                                },
                            },
                            "avoid_list": {"type": "array"},
                            "late_news_alerts": {"type": "array"},
                        },
                    }
                },
            },
            metadata_tags=["nfl", "sunday", "slate", "correlations", "weather"],
        )

    def _nba_props_template(self) -> ScenarioTemplate:
        """NBA player props analysis template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.NBA_PROPS_NIGHT,
            instructions="""You are EQ12 NBA Props Specialist. Analyze player props using:

1. Usage Rate Analysis: Track player usage changes with lineup variations
2. Pace Metrics: Factor in team pace, back-to-back impacts, rest advantages
3. Matchup Advantages: Identify defensive weaknesses and exploitation opportunities
4. Line Shopping: Compare props across books for best numbers and Alt lines
5. Correlation Plays: Build same-game parlays with positive correlation
6. Load Management: Monitor rest patterns and coach tendencies
7. Injury Chains: Analyze how injuries create usage bumps for teammates

Focus on high-volume, data-driven prop selections with clear edge identification.""",
            tools=[ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER, ToolType.FUNCTION],
            config=ResponseConfig(
                model="gpt-4o",
                temperature=0.05,  # Lower temp for statistical analysis
                max_output_tokens=3500,
                stream=True,
                service_tier=ServiceTier.DEFAULT,
            ),
            output_schema={
                "type": "object",
                "properties": {
                    "nba_props_analysis": {
                        "type": "object",
                        "properties": {
                            "market_overview": {
                                "type": "object",
                                "properties": {
                                    "total_props_analyzed": {"type": "integer"},
                                    "injury_impacts": {"type": "array"},
                                    "pace_factors": {"type": "array"},
                                    "line_movement_alerts": {"type": "array"},
                                },
                            },
                            "top_props": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "player": {"type": "string"},
                                        "prop_market": {"type": "string"},
                                        "line": {"type": "number"},
                                        "selection": {"type": "string"},
                                        "odds": {"type": "number"},
                                        "fair_value": {"type": "number"},
                                        "edge_percentage": {"type": "number"},
                                        "confidence": {"type": "string"},
                                        "unit_size": {"type": "number"},
                                        "key_factors": {"type": "array"},
                                    },
                                },
                            },
                            "correlation_parlays": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "game": {"type": "string"},
                                        "legs": {"type": "array"},
                                        "correlation_type": {"type": "string"},
                                        "parlay_odds": {"type": "number"},
                                        "expected_value": {"type": "number"},
                                    },
                                },
                            },
                            "alternative_lines": {"type": "array"},
                            "hedge_opportunities": {"type": "array"},
                        },
                    }
                },
            },
            metadata_tags=["nba", "props", "players", "correlations", "usage"],
        )

    def _march_madness_template(self) -> ScenarioTemplate:
        """March Madness bracket analysis template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.MARCH_MADNESS_BRACKET,
            instructions="""You are EQ12 March Madness Analyst. Provide bracket analysis using:

1. Seed Performance: Historical seed performance and upset patterns
2. Conference Strength: Analyze conference tournament performance
3. Bracket Busting: Identify potential upset candidates
4. Value Betting: Find overvalued/undervalued teams in futures markets
5. Regional Analysis: Break down each region's path to Final Four
6. Injury Impact: Monitor key player health entering tournament
7. Coaching Edge: Evaluate tournament coaching experience

Focus on data-driven picks with clear reasoning for bracket construction.""",
            tools=[ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER, ToolType.FUNCTION],
            config=ResponseConfig(
                model="gpt-4o",
                temperature=0.1,
                max_output_tokens=4000,
                stream=True,
                service_tier=ServiceTier.DEFAULT,
            ),
            output_schema={
                "type": "object",
                "properties": {
                    "bracket_analysis": {
                        "type": "object",
                        "properties": {
                            "region_breakdown": {"type": "array"},
                            "upset_picks": {"type": "array"},
                            "final_four_teams": {"type": "array"},
                            "champion_pick": {"type": "string"},
                            "value_bets": {"type": "array"},
                            "key_matchups": {"type": "array"},
                        },
                    }
                },
            },
            metadata_tags=["ncaa", "basketball", "tournament", "bracket", "upsets"],
        )

    def _live_momentum_template(self) -> ScenarioTemplate:
        """Live betting momentum analysis template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.LIVE_GAME_MOMENTUM,
            instructions="""You are EQ12 Live Betting Specialist. Analyze in-game momentum with:

1. Win Probability Tracking: Real-time win probability vs live odds discrepancies
2. Momentum Indicators: Scoring runs, turnovers, foul trouble, timeout usage
3. Regression Opportunities: Identify overreactions to small sample events
4. Clock Management: Factor in time/score situations and game theory
5. Referee Impact: Track officiating tendencies affecting spread/totals
6. Closing Line Value: Compare live prices to projected closing numbers
7. Cash Out Timing: Optimal hedge and cash-out decision points

Execute rapid analysis for time-sensitive opportunities with clear entry/exit points.""",
            tools=[ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER],
            config=ResponseConfig(
                model="gpt-4o",
                temperature=0.2,
                max_output_tokens=2000,
                stream=True,
                service_tier=ServiceTier.PRIORITY,  # Priority for time-sensitive
                background=False,  # Immediate response needed
            ),
            output_schema={
                "type": "object",
                "properties": {
                    "live_analysis": {
                        "type": "object",
                        "properties": {
                            "current_situation": {
                                "type": "object",
                                "properties": {
                                    "game": {"type": "string"},
                                    "time_remaining": {"type": "string"},
                                    "score": {"type": "string"},
                                    "live_spread": {"type": "number"},
                                    "live_total": {"type": "number"},
                                    "momentum_indicator": {"type": "string"},
                                },
                            },
                            "immediate_opportunities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "market": {"type": "string"},
                                        "selection": {"type": "string"},
                                        "current_odds": {"type": "number"},
                                        "fair_value": {"type": "number"},
                                        "urgency": {"type": "string"},
                                        "max_stake": {"type": "number"},
                                        "exit_strategy": {"type": "string"},
                                    },
                                },
                            },
                            "hedge_alerts": {"type": "array"},
                            "cash_out_recommendations": {"type": "array"},
                            "avoid_traps": {"type": "array"},
                        },
                    }
                },
            },
            metadata_tags=["live", "momentum", "urgency", "hedge", "timing"],
        )

    def _steam_alert_template(self) -> ScenarioTemplate:
        """Sharp steam move alert template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.SHARP_STEAM_ALERT,
            instructions="""You are EQ12 Steam Detection System. Identify sharp money moves using:

1. Reverse Line Movement: Prices moving against public betting percentages
2. Volume Analysis: Unusual betting volume spikes at specific books
3. Timing Patterns: Professional betting windows and synchronization
4. Book Behavior: Limit reductions, line pulls, and odds adjustments
5. CLV Prediction: Forecast where lines will close based on steam direction
6. Follow Protocols: Optimal timing and sizing for steam-following strategies

Provide immediate alerts with confidence levels and execution recommendations.""",
            tools=[ToolType.WEB_SEARCH, ToolType.FUNCTION],
            config=ResponseConfig(
                model="gpt-4o",
                temperature=0.0,  # Deterministic for detection algorithms
                max_output_tokens=1500,
                stream=True,
                service_tier=ServiceTier.PRIORITY,
                background=False,
            ),
            output_schema={
                "type": "object",
                "properties": {
                    "steam_alert": {
                        "type": "object",
                        "properties": {
                            "alert_level": {
                                "type": "string",
                                "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                            },
                            "detected_moves": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "game": {"type": "string"},
                                        "market": {"type": "string"},
                                        "direction": {"type": "string"},
                                        "line_movement": {"type": "number"},
                                        "public_percentage": {"type": "number"},
                                        "sharp_indicators": {"type": "array"},
                                        "confidence_score": {"type": "number"},
                                        "follow_recommendation": {"type": "string"},
                                    },
                                },
                            },
                            "execution_plan": {
                                "type": "object",
                                "properties": {
                                    "immediate_actions": {"type": "array"},
                                    "optimal_books": {"type": "array"},
                                    "sizing_recommendations": {"type": "array"},
                                    "time_window": {"type": "string"},
                                },
                            },
                            "risk_warnings": {"type": "array"},
                        },
                    }
                },
            },
            metadata_tags=["steam", "sharp", "alerts", "timing", "execution"],
        )

    def _kelly_manager_template(self) -> ScenarioTemplate:
        """Kelly criterion bankroll management template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.KELLY_BANKROLL_MANAGER,
            instructions="""You are EQ12 Bankroll Manager using Kelly Criterion optimization:

1. Edge Calculation: Determine true edge for each betting opportunity
2. Kelly Sizing: Calculate optimal bet size using Kelly formula
3. Fractional Kelly: Apply conservative fractions (0.25x - 0.5x Kelly) for safety
4. Correlation Adjustments: Reduce sizing for correlated positions
5. Drawdown Management: Dynamic sizing based on recent performance
6. Portfolio Heat: Monitor total risk exposure across all positions
7. Rebalancing: Adjust position sizes as bankroll fluctuates

Provide precise sizing recommendations with risk management safeguards.""",
            tools=[ToolType.CODE_INTERPRETER, ToolType.FUNCTION],
            config=ResponseConfig(
                model="gpt-4o",
                temperature=0.0,  # Deterministic for financial calculations
                max_output_tokens=2500,
                service_tier=ServiceTier.DEFAULT,
            ),
            output_schema={
                "type": "object",
                "properties": {
                    "bankroll_management": {
                        "type": "object",
                        "properties": {
                            "current_status": {
                                "type": "object",
                                "properties": {
                                    "total_bankroll": {"type": "number"},
                                    "available_capital": {"type": "number"},
                                    "positions_count": {"type": "integer"},
                                    "portfolio_heat": {"type": "number"},
                                    "recent_roi": {"type": "number"},
                                    "drawdown_status": {"type": "string"},
                                },
                            },
                            "sizing_recommendations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "opportunity_id": {"type": "string"},
                                        "estimated_edge": {"type": "number"},
                                        "full_kelly": {"type": "number"},
                                        "recommended_kelly": {"type": "number"},
                                        "stake_amount": {"type": "number"},
                                        "max_loss": {"type": "number"},
                                        "correlation_adjustment": {"type": "number"},
                                    },
                                },
                            },
                            "risk_metrics": {
                                "type": "object",
                                "properties": {
                                    "portfolio_volatility": {"type": "number"},
                                    "value_at_risk": {"type": "number"},
                                    "expected_growth_rate": {"type": "number"},
                                    "ruin_probability": {"type": "number"},
                                },
                            },
                            "alerts": {"type": "array"},
                        },
                    }
                },
            },
            metadata_tags=["kelly", "bankroll", "sizing", "risk", "optimization"],
        )

    def _playoff_hedge_template(self) -> ScenarioTemplate:
        """Playoff series hedge template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.PLAYOFF_SERIES_HEDGE,
            instructions="""Analyze playoff series hedging opportunities with dynamic position management.""",
            tools=[ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER],
            config=ResponseConfig(model="gpt-4o", temperature=0.1, max_output_tokens=2000),
            output_schema={"type": "object", "properties": {"hedge_analysis": {"type": "object"}}},
            metadata_tags=["playoffs", "hedge", "series", "risk-management"],
        )

    def _weather_totals_template(self) -> ScenarioTemplate:
        """Weather impact on totals template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.WEATHER_IMPACT_TOTALS,
            instructions="""Analyze weather impact on game totals and player performance.""",
            tools=[ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER],
            config=ResponseConfig(model="gpt-4o", temperature=0.1, max_output_tokens=2000),
            output_schema={
                "type": "object",
                "properties": {"weather_analysis": {"type": "object"}},
            },
            metadata_tags=["weather", "totals", "outdoor", "conditions"],
        )

    def _injury_reaction_template(self) -> ScenarioTemplate:
        """Injury news reaction template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.INJURY_NEWS_REACTION,
            instructions="""React to breaking injury news with line movement predictions.""",
            tools=[ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER],
            config=ResponseConfig(model="gpt-4o", temperature=0.1, max_output_tokens=2000),
            output_schema={"type": "object", "properties": {"injury_analysis": {"type": "object"}}},
            metadata_tags=["injury", "news", "reaction", "line-movement"],
        )

    def _arbitrage_template(self) -> ScenarioTemplate:
        """Arbitrage opportunities template"""
        return ScenarioTemplate(
            scenario_type=BettingScenario.ARBITRAGE_SCANNER,
            instructions="""Identify risk-free arbitrage opportunities across sportsbooks.""",
            tools=[ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER],
            config=ResponseConfig(model="gpt-4o", temperature=0.1, max_output_tokens=2000),
            output_schema={
                "type": "object",
                "properties": {"arbitrage_analysis": {"type": "object"}},
            },
            metadata_tags=["arbitrage", "risk-free", "sportsbooks", "opportunities"],
        )

    async def execute_scenario(
        self,
        scenario: BettingScenario,
        context_data: dict[str, Any],
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute a pre-configured betting scenario template"""

        if scenario not in self.templates:
            raise ValueError(f"Scenario {scenario} not found in templates")

        template = self.templates[scenario]

        # Build the payload using template configuration
        payload = {
            "model": template.config.model,
            "instructions": template.instructions,
            "input": [
                {"type": "text", "text": self._format_context_for_scenario(scenario, context_data)}
            ],
            "tools": self.api._prepare_tools(template.tools),
            "text": {"type": "json_object", "json_schema": template.output_schema},
            "temperature": template.config.temperature,
            "max_output_tokens": template.config.max_output_tokens,
            "stream": template.config.stream,
            "background": template.config.background,
            "service_tier": template.config.service_tier.value,
            "metadata": {
                "scenario_type": scenario.value,
                "tags": ",".join(template.metadata_tags),
                **context_data.get("metadata", {}),
            },
        }

        if conversation_id:
            payload["conversation"] = conversation_id

        return await self.api._make_request(payload)

    def _format_context_for_scenario(
        self, scenario: BettingScenario, context: dict[str, Any]
    ) -> str:
        """Format context data for specific scenario"""

        if scenario == BettingScenario.NFL_SUNDAY_SLATE:
            return f"""Analyze NFL Sunday slate:

Games: {json.dumps(context.get("games", []), indent=2)}
Weather: {json.dumps(context.get("weather", []), indent=2)}
Injuries: {json.dumps(context.get("injuries", []), indent=2)}
Bankroll: ${context.get("bankroll", 1000):,.2f}

Provide comprehensive slate analysis with correlation opportunities."""

        elif scenario == BettingScenario.NBA_PROPS_NIGHT:
            return f"""Analyze NBA player props:

Games: {json.dumps(context.get("games", []), indent=2)}
Players: {json.dumps(context.get("players", []), indent=2)}
Props Available: {json.dumps(context.get("props", []), indent=2)}
Injury Reports: {json.dumps(context.get("injuries", []), indent=2)}

Focus on high-edge props with usage rate advantages."""

        elif scenario == BettingScenario.LIVE_GAME_MOMENTUM:
            return f"""Analyze live game situation:

Game State: {json.dumps(context.get("game_state", {}), indent=2)}
Live Lines: {json.dumps(context.get("live_lines", {}), indent=2)}
Momentum Factors: {json.dumps(context.get("momentum", []), indent=2)}

Identify immediate betting opportunities and hedge points."""

        elif scenario == BettingScenario.SHARP_STEAM_ALERT:
            return f"""Detect sharp steam moves:

Line Movements: {json.dumps(context.get("line_moves", []), indent=2)}
Volume Data: {json.dumps(context.get("volume", []), indent=2)}
Public Percentages: {json.dumps(context.get("public_bets", []), indent=2)}

Identify professional betting activity and follow opportunities."""

        elif scenario == BettingScenario.KELLY_BANKROLL_MANAGER:
            return f"""Manage bankroll with Kelly optimization:

Current Bankroll: ${context.get("bankroll", 1000):,.2f}
Open Positions: {json.dumps(context.get("positions", []), indent=2)}
New Opportunities: {json.dumps(context.get("opportunities", []), indent=2)}
Risk Tolerance: {context.get("risk_tolerance", "moderate")}

Calculate optimal position sizing with risk management."""

        else:
            # Generic context formatting
            return f"""Analyze betting scenario: {scenario.value}

Context Data:
{json.dumps(context, indent=2)}

Provide analysis and recommendations."""


# Convenience functions for template execution
async def analyze_nfl_sunday_slate(
    games: list[dict],
    weather: list[dict] | None = None,
    injuries: list[dict] | None = None,
    bankroll: float = 1000.0,
) -> dict[str, Any]:
    """Analyze NFL Sunday slate using template"""
    templates = EQ12ResponseTemplates()

    context = {
        "games": games,
        "weather": weather or [],
        "injuries": injuries or [],
        "bankroll": bankroll,
    }

    return await templates.execute_scenario(BettingScenario.NFL_SUNDAY_SLATE, context)


async def analyze_nba_props_night(
    games: list[dict],
    props: list[dict],
    players: list[dict] | None = None,
    injuries: list[dict] | None = None,
) -> dict[str, Any]:
    """Analyze NBA props using template"""
    templates = EQ12ResponseTemplates()

    context = {"games": games, "props": props, "players": players or [], "injuries": injuries or []}

    return await templates.execute_scenario(BettingScenario.NBA_PROPS_NIGHT, context)


async def detect_steam_moves(
    line_movements: list[dict],
    volume_data: list[dict] | None = None,
    public_percentages: list[dict] | None = None,
) -> dict[str, Any]:
    """Detect sharp steam moves using template"""
    templates = EQ12ResponseTemplates()

    context = {
        "line_moves": line_movements,
        "volume": volume_data or [],
        "public_bets": public_percentages or [],
    }

    return await templates.execute_scenario(BettingScenario.SHARP_STEAM_ALERT, context)


async def optimize_bankroll_kelly(
    bankroll: float,
    positions: list[dict],
    opportunities: list[dict],
    risk_tolerance: str = "moderate",
) -> dict[str, Any]:
    """Optimize bankroll using Kelly criterion template"""
    templates = EQ12ResponseTemplates()

    context = {
        "bankroll": bankroll,
        "positions": positions,
        "opportunities": opportunities,
        "risk_tolerance": risk_tolerance,
    }

    return await templates.execute_scenario(BettingScenario.KELLY_BANKROLL_MANAGER, context)


if __name__ == "__main__":
    import asyncio

    async def test_templates():
        """Test response templates"""
        print("🧪 Testing EQ12 Response Templates")

        # Test NFL Sunday template
        sample_games = [
            {"home": "Patriots", "away": "Bills", "spread": "Bills -3.5", "total": 44.5},
            {"home": "Cowboys", "away": "Eagles", "spread": "Eagles -7", "total": 51.5},
        ]

        try:
            result = await analyze_nfl_sunday_slate(games=sample_games, bankroll=5000.0)

            print(f"✅ NFL Template Response ID: {result.get('id')}")

        except Exception as e:
            print(f"❌ Template test failed: {e}")

    asyncio.run(test_templates())
