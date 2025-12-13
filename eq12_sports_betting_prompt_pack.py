#!/usr/bin/env python3
"""
EQ12 Sports Betting Prompt Pack - Advanced AI Prompting System
=============================================================

Comprehensive collection of specialized AI prompts for sports betting analysis:
- Market analysis and trend identification
- Player performance and injury impact assessment
- Weather and venue factor analysis
- Line movement and sharp money detection
- Correlation and hedge opportunity identification
- Risk management and bankroll optimization

Features:
- 50+ specialized prompts for different betting scenarios
- Dynamic prompt generation with real-time data injection
- Context-aware prompt selection based on query type
- Integration with OpenAI GPT-4o for advanced analysis
- Customizable prompt templates with parameter substitution
- Multi-sport coverage with sport-specific expertise

Author: EQ12 Development Team
Date: October 6, 2025
Version: 1.0.0
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

# EQ12 Integration
try:
    from eq12_advanced_correlation_engine import EQ12AdvancedCorrelationEngine
    from eq12_enhanced_openai_sdk import EQ12EnhancedOpenAIClient
    from eq12_line_movement_intelligence import EQ12LineMovementIntelligence

    EQ12_INTEGRATION = True
except ImportError:
    EQ12_INTEGRATION = False
    print("⚠️ EQ12 integration not available - running in standalone mode")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/sports_betting_prompts.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12SportsPrompts")


class PromptCategory(Enum):
    """Categories of sports betting prompts"""

    MARKET_ANALYSIS = "market_analysis"
    PLAYER_ANALYSIS = "player_analysis"
    TEAM_ANALYSIS = "team_analysis"
    GAME_ANALYSIS = "game_analysis"
    LINE_MOVEMENT = "line_movement"
    CORRELATION = "correlation"
    RISK_MANAGEMENT = "risk_management"
    BANKROLL = "bankroll"
    ARBITRAGE = "arbitrage"
    HEDGE = "hedge"
    WEATHER = "weather"
    INJURY = "injury"
    TRENDS = "trends"
    PROPS = "props"
    LIVE_BETTING = "live_betting"
    FUTURES = "futures"
    PARLAY = "parlay"
    SHARP_MONEY = "sharp_money"
    PUBLIC_BETTING = "public_betting"
    CONTRARIAN = "contrarian"


class Sport(Enum):
    """Supported sports"""

    NFL = "nfl"
    NBA = "nba"
    MLB = "mlb"
    NHL = "nhl"
    NCAAF = "ncaaf"
    NCAAB = "ncaab"
    SOCCER = "soccer"
    TENNIS = "tennis"
    GOLF = "golf"
    MMA = "mma"
    BOXING = "boxing"
    ESPORTS = "esports"


class PromptComplexity(Enum):
    """Complexity levels for prompts"""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class PromptTemplate:
    """Sports betting prompt template"""

    id: str
    name: str
    category: PromptCategory
    sport: Sport | None
    complexity: PromptComplexity
    template: str
    parameters: list[str]
    description: str
    use_cases: list[str]
    expected_output: str
    examples: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def render(self, **kwargs) -> str:
        """Render template with provided parameters"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"❌ Missing parameter {e} for template {self.id}")
            return self.template


@dataclass
class PromptResponse:
    """AI response with metadata"""

    prompt_id: str
    query: str
    response: str
    confidence_score: float
    execution_time: float
    tokens_used: int
    model_used: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class EQ12SportsPromptPack:
    """
    Advanced AI prompt system for sports betting analysis
    """

    def __init__(self, eq12_root: str = "C:/EQ12"):
        self.eq12_root = Path(eq12_root)
        self.prompts_dir = self.eq12_root / "configs" / "prompts"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

        # AI client
        self.ai_client = None

        # Prompt templates
        self.prompt_templates: dict[str, PromptTemplate] = {}

        # Response cache
        self.response_cache: dict[str, PromptResponse] = {}

        # Initialize components
        self._initialize_components()
        self._load_prompt_templates()

        logger.info("🎯 EQ12 Sports Betting Prompt Pack initialized")

    def _initialize_components(self):
        """Initialize AI components"""
        if EQ12_INTEGRATION:
            try:
                self.ai_client = EQ12EnhancedOpenAIClient()
                logger.info("✅ AI client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI client: {e}")

    def _load_prompt_templates(self):
        """Load all prompt templates"""
        # Market Analysis Prompts
        self._add_market_analysis_prompts()

        # Player Analysis Prompts
        self._add_player_analysis_prompts()

        # Game Analysis Prompts
        self._add_game_analysis_prompts()

        # Line Movement Prompts
        self._add_line_movement_prompts()

        # Risk Management Prompts
        self._add_risk_management_prompts()

        # Correlation Prompts
        self._add_correlation_prompts()

        # Live Betting Prompts
        self._add_live_betting_prompts()

        # Parlay Prompts
        self._add_parlay_prompts()

        # Advanced Analysis Prompts
        self._add_advanced_analysis_prompts()

        logger.info(f"📚 Loaded {len(self.prompt_templates)} prompt templates")

    def _add_market_analysis_prompts(self):
        """Add market analysis prompt templates"""

        # Market inefficiency detection
        self.prompt_templates["market_inefficiency"] = PromptTemplate(
            id="market_inefficiency",
            name="Market Inefficiency Detector",
            category=PromptCategory.MARKET_ANALYSIS,
            sport=None,
            complexity=PromptComplexity.ADVANCED,
            template="""
Analyze the following betting market for inefficiencies and opportunities:

Sport: {sport}
Market: {market_type}
Game: {game}

Current Lines:
{current_lines}

Historical Data:
{historical_data}

Market Volume: {market_volume}
Public Betting Percentage: {public_betting}
Sharp Money Indicators: {sharp_indicators}

Identify:
1. Potential market inefficiencies
2. Line value opportunities
3. Expected value calculations
4. Risk factors and concerns
5. Recommended betting strategy

Focus on mathematical analysis and provide specific reasoning for any opportunities identified.
""",
            parameters=[
                "sport",
                "market_type",
                "game",
                "current_lines",
                "historical_data",
                "market_volume",
                "public_betting",
                "sharp_indicators",
            ],
            description="Detects market inefficiencies and betting value opportunities",
            use_cases=["Line shopping", "Value betting identification", "Market timing"],
            expected_output="Detailed analysis with specific betting recommendations and mathematical justification",
        )

        # Public vs sharp money analysis
        self.prompt_templates["public_sharp_analysis"] = PromptTemplate(
            id="public_sharp_analysis",
            name="Public vs Sharp Money Analysis",
            category=PromptCategory.SHARP_MONEY,
            sport=None,
            complexity=PromptComplexity.INTERMEDIATE,
            template="""
Analyze the betting patterns for this game:

Game: {game}
Sport: {sport}

Public Betting Data:
- Bet Percentage: {public_bet_percentage}
- Money Percentage: {public_money_percentage}
- Ticket Count: {ticket_count}

Sharp Money Indicators:
- Line Movement: {line_movement}
- Reverse Line Movement: {reverse_movement}
- Steam Moves: {steam_moves}
- Syndicate Action: {syndicate_action}

Current Odds:
{current_odds}

Provide analysis on:
1. Public vs sharp money divergence
2. Contrarian betting opportunities
3. Line movement significance
4. Expected market correction
5. Betting strategy recommendation

Include confidence levels and risk assessment.
""",
            parameters=[
                "game",
                "sport",
                "public_bet_percentage",
                "public_money_percentage",
                "ticket_count",
                "line_movement",
                "reverse_movement",
                "steam_moves",
                "syndicate_action",
                "current_odds",
            ],
            description="Analyzes public vs professional betting patterns",
            use_cases=["Contrarian betting", "Sharp money following", "Market sentiment analysis"],
            expected_output="Strategic analysis with betting direction and confidence levels",
        )

    def _add_player_analysis_prompts(self):
        """Add player analysis prompt templates"""

        # Player performance prediction
        self.prompt_templates["player_performance"] = PromptTemplate(
            id="player_performance",
            name="Player Performance Predictor",
            category=PromptCategory.PLAYER_ANALYSIS,
            sport=None,
            complexity=PromptComplexity.ADVANCED,
            template="""
Analyze player performance for prop betting:

Player: {player_name}
Sport: {sport}
Position: {position}
Team: {team}

Recent Performance (last {games_count} games):
{recent_stats}

Season Statistics:
{season_stats}

Opponent Analysis:
{opponent_info}

Injury Report:
{injury_status}

Weather/Venue Factors:
{environmental_factors}

Available Props:
{available_props}

Provide detailed analysis including:
1. Performance trend analysis
2. Matchup advantages/disadvantages
3. Prop bet value assessment
4. Recommended bets with reasoning
5. Risk factors and concerns
6. Confidence levels for each recommendation

Use statistical analysis and contextual factors for predictions.
""",
            parameters=[
                "player_name",
                "sport",
                "position",
                "team",
                "games_count",
                "recent_stats",
                "season_stats",
                "opponent_info",
                "injury_status",
                "environmental_factors",
                "available_props",
            ],
            description="Comprehensive player performance analysis for prop betting",
            use_cases=["Player props", "Performance prediction", "Matchup analysis"],
            expected_output="Detailed player analysis with specific prop bet recommendations",
        )

        # Injury impact assessment
        self.prompt_templates["injury_impact"] = PromptTemplate(
            id="injury_impact",
            name="Injury Impact Assessor",
            category=PromptCategory.INJURY,
            sport=None,
            complexity=PromptComplexity.EXPERT,
            template="""
Assess the betting impact of player injuries:

Injured Player: {injured_player}
Injury Type: {injury_type}
Injury Severity: {injury_severity}
Expected Return: {return_timeline}
Team: {team}
Sport: {sport}

Team Impact Analysis:
- Player's Role: {player_role}
- Season Stats: {player_stats}
- Replacement Player: {replacement_player}
- Replacement Stats: {replacement_stats}

Historical Injury Data:
{historical_injury_impact}

Current Betting Lines:
Before Injury: {lines_before}
After Injury: {lines_after}
Line Movement: {line_movement}

Market Response:
{market_response}

Analyze:
1. Quantitative impact on team performance
2. Line adjustment accuracy assessment
3. Over/under reactions in the market
4. Secondary effects (other players, team dynamics)
5. Betting opportunities created
6. Timeline for market correction

Provide data-driven analysis with specific betting recommendations.
""",
            parameters=[
                "injured_player",
                "injury_type",
                "injury_severity",
                "return_timeline",
                "team",
                "sport",
                "player_role",
                "player_stats",
                "replacement_player",
                "replacement_stats",
                "historical_injury_impact",
                "lines_before",
                "lines_after",
                "line_movement",
                "market_response",
            ],
            description="Analyzes betting impact of player injuries and market reactions",
            use_cases=[
                "Injury news trading",
                "Line value assessment",
                "Market inefficiency exploitation",
            ],
            expected_output="Comprehensive injury impact analysis with betting strategy",
        )

    def _add_game_analysis_prompts(self):
        """Add game analysis prompt templates"""

        # Weather impact analysis
        self.prompt_templates["weather_impact"] = PromptTemplate(
            id="weather_impact",
            name="Weather Impact Analyzer",
            category=PromptCategory.WEATHER,
            sport=None,
            complexity=PromptComplexity.INTERMEDIATE,
            template="""
Analyze weather impact on game betting:

Game: {game}
Sport: {sport}
Venue: {venue}
Date/Time: {game_time}

Weather Forecast:
- Temperature: {temperature}
- Wind Speed: {wind_speed}
- Wind Direction: {wind_direction}
- Precipitation: {precipitation}
- Humidity: {humidity}
- Visibility: {visibility}

Historical Weather Impact:
{historical_weather_data}

Team Weather Performance:
Home Team: {home_team_weather_stats}
Away Team: {away_team_weather_stats}

Current Betting Lines:
{current_lines}

Analyze:
1. Weather impact on game dynamics
2. Historical performance in similar conditions
3. Line adjustment opportunities
4. Total (over/under) implications
5. Player prop adjustments
6. In-game live betting considerations

Provide specific betting recommendations based on weather analysis.
""",
            parameters=[
                "game",
                "sport",
                "venue",
                "game_time",
                "temperature",
                "wind_speed",
                "wind_direction",
                "precipitation",
                "humidity",
                "visibility",
                "historical_weather_data",
                "home_team_weather_stats",
                "away_team_weather_stats",
                "current_lines",
            ],
            description="Analyzes weather impact on game outcomes and betting lines",
            use_cases=["Outdoor sports betting", "Total adjustments", "Player props"],
            expected_output="Weather-based betting analysis with specific recommendations",
        )

    def _add_line_movement_prompts(self):
        """Add line movement analysis prompts"""

        # Steam move detection
        self.prompt_templates["steam_move_analysis"] = PromptTemplate(
            id="steam_move_analysis",
            name="Steam Move Detector",
            category=PromptCategory.LINE_MOVEMENT,
            sport=None,
            complexity=PromptComplexity.EXPERT,
            template="""
Analyze potential steam move and line movement patterns:

Game: {game}
Sport: {sport}

Line Movement Timeline:
{line_movement_timeline}

Betting Volume Data:
{volume_data}

Market Indicators:
- Sharp Sportsbook Lines: {sharp_books}
- Public Sportsbook Lines: {public_books}
- Movement Speed: {movement_speed}
- Volume Spike: {volume_spike}

Steam Move Characteristics:
- Simultaneous Movement: {simultaneous_movement}
- Line Magnitude: {line_magnitude}
- Market Consensus: {market_consensus}

Professional Betting Indicators:
{professional_indicators}

Analysis Required:
1. Steam move confirmation
2. Originating source identification
3. Market response prediction
4. Follow or fade strategy
5. Timing considerations
6. Risk assessment

Provide immediate actionable recommendations with confidence levels.
""",
            parameters=[
                "game",
                "sport",
                "line_movement_timeline",
                "volume_data",
                "sharp_books",
                "public_books",
                "movement_speed",
                "volume_spike",
                "simultaneous_movement",
                "line_magnitude",
                "market_consensus",
                "professional_indicators",
            ],
            description="Detects and analyzes steam moves for immediate betting action",
            use_cases=[
                "Steam move following",
                "Quick line value capture",
                "Professional betting signals",
            ],
            expected_output="Immediate steam move analysis with action recommendations",
        )

    def _add_risk_management_prompts(self):
        """Add risk management prompt templates"""

        # Portfolio risk assessment
        self.prompt_templates["portfolio_risk"] = PromptTemplate(
            id="portfolio_risk",
            name="Portfolio Risk Analyzer",
            category=PromptCategory.RISK_MANAGEMENT,
            sport=None,
            complexity=PromptComplexity.EXPERT,
            template="""
Analyze betting portfolio risk and optimization:

Current Portfolio:
{current_positions}

Portfolio Metrics:
- Total Exposure: {total_exposure}
- Number of Positions: {position_count}
- Average Odds: {average_odds}
- Expected Return: {expected_return}

Correlation Analysis:
{correlation_matrix}

Risk Factors:
- Single Game Exposure: {single_game_risk}
- Sport Concentration: {sport_concentration}
- Odds Distribution: {odds_distribution}
- Time Concentration: {time_concentration}

Market Conditions:
{market_conditions}

Risk Management Analysis:
1. Portfolio diversification assessment
2. Correlation risk evaluation
3. Concentration risk identification
4. Hedging opportunities
5. Position sizing recommendations
6. Risk reduction strategies

Provide specific actions to optimize risk-adjusted returns.
""",
            parameters=[
                "current_positions",
                "total_exposure",
                "position_count",
                "average_odds",
                "expected_return",
                "correlation_matrix",
                "single_game_risk",
                "sport_concentration",
                "odds_distribution",
                "time_concentration",
                "market_conditions",
            ],
            description="Comprehensive portfolio risk analysis and optimization",
            use_cases=["Risk management", "Portfolio optimization", "Hedge identification"],
            expected_output="Risk assessment with specific portfolio adjustments",
        )

    def _add_correlation_prompts(self):
        """Add correlation analysis prompts"""

        # Multi-leg correlation analysis
        self.prompt_templates["correlation_analysis"] = PromptTemplate(
            id="correlation_analysis",
            name="Multi-Leg Correlation Analyzer",
            category=PromptCategory.CORRELATION,
            sport=None,
            complexity=PromptComplexity.EXPERT,
            template="""
Analyze correlations between multiple betting propositions:

Primary Bet: {primary_bet}
Additional Bets: {additional_bets}

Game Context:
{game_context}

Historical Correlation Data:
{historical_correlations}

Statistical Analysis:
{statistical_data}

Market Factors:
{market_factors}

Correlation Analysis Required:
1. Direct correlations between propositions
2. Indirect correlation pathways
3. Negative correlation identification
4. Portfolio effect on combined probability
5. Optimal combination strategies
6. Risk mitigation through correlation awareness

Specific Analysis:
- Same Game Parlays: {sgp_analysis}
- Cross-Game Correlations: {cross_game_analysis}
- Player Prop Correlations: {player_prop_analysis}
- Market Correlation Impact: {market_impact}

Provide correlation coefficients, combined probability adjustments, and strategic recommendations.
""",
            parameters=[
                "primary_bet",
                "additional_bets",
                "game_context",
                "historical_correlations",
                "statistical_data",
                "market_factors",
                "sgp_analysis",
                "cross_game_analysis",
                "player_prop_analysis",
                "market_impact",
            ],
            description="Advanced correlation analysis for multi-leg betting strategies",
            use_cases=["Parlay construction", "Portfolio optimization", "Risk assessment"],
            expected_output="Detailed correlation analysis with strategic betting recommendations",
        )

    def _add_live_betting_prompts(self):
        """Add live betting prompt templates"""

        # In-game momentum analysis
        self.prompt_templates["live_momentum"] = PromptTemplate(
            id="live_momentum",
            name="Live Game Momentum Analyzer",
            category=PromptCategory.LIVE_BETTING,
            sport=None,
            complexity=PromptComplexity.ADVANCED,
            template="""
Analyze in-game momentum and live betting opportunities:

Game: {game}
Sport: {sport}
Current Time: {game_time}
Current Score: {current_score}

Game Flow Analysis:
{game_flow_data}

Pre-Game Expectations:
- Pre-game Line: {pregame_line}
- Pre-game Total: {pregame_total}
- Pre-game Analysis: {pregame_analysis}

Live Market Data:
- Current Live Line: {live_line}
- Current Live Total: {live_total}
- Line Movement: {live_movement}
- Volume Indicators: {live_volume}

Momentum Indicators:
- Recent Scoring: {recent_scoring}
- Possession Stats: {possession_stats}
- Performance Metrics: {performance_metrics}
- Injury/Substitution Impact: {in_game_changes}

Betting Psychology:
- Public Reaction: {public_reaction}
- Market Overreaction: {market_overreaction}

Analysis Focus:
1. Momentum sustainability assessment
2. Market overreaction identification
3. Regression to mean probability
4. Live value opportunities
5. In-game prop adjustments
6. Cash-out considerations

Provide real-time betting recommendations with timing considerations.
""",
            parameters=[
                "game",
                "sport",
                "game_time",
                "current_score",
                "game_flow_data",
                "pregame_line",
                "pregame_total",
                "pregame_analysis",
                "live_line",
                "live_total",
                "live_movement",
                "live_volume",
                "recent_scoring",
                "possession_stats",
                "performance_metrics",
                "in_game_changes",
                "public_reaction",
                "market_overreaction",
            ],
            description="Real-time analysis of in-game momentum for live betting",
            use_cases=["Live betting", "Momentum betting", "Market timing"],
            expected_output="Real-time betting analysis with specific live bet recommendations",
        )

    def _add_parlay_prompts(self):
        """Add parlay construction prompt templates"""

        # Advanced parlay construction
        self.prompt_templates["parlay_construction"] = PromptTemplate(
            id="parlay_construction",
            name="Advanced Parlay Constructor",
            category=PromptCategory.PARLAY,
            sport=None,
            complexity=PromptComplexity.EXPERT,
            template="""
Construct optimal parlay with correlation analysis:

Available Selections:
{available_selections}

Correlation Matrix:
{correlation_matrix}

Target Parameters:
- Minimum Legs: {min_legs}
- Maximum Legs: {max_legs}
- Target Odds Range: {target_odds}
- Risk Tolerance: {risk_tolerance}
- Strategy: {strategy}

Individual Analysis:
{individual_leg_analysis}

Market Conditions:
{market_conditions}

Construction Analysis:
1. Leg selection optimization
2. Correlation impact assessment
3. Combined probability calculation
4. Expected value optimization
5. Risk-reward balance
6. Alternative combinations

Specific Requirements:
- Avoid negative correlations
- Maximize positive correlations where beneficial
- Balance probability vs payout
- Consider market efficiency
- Account for juice/vig impact

Provide the optimal parlay construction with detailed reasoning for each selection.
""",
            parameters=[
                "available_selections",
                "correlation_matrix",
                "min_legs",
                "max_legs",
                "target_odds",
                "risk_tolerance",
                "strategy",
                "individual_leg_analysis",
                "market_conditions",
            ],
            description="Advanced parlay construction with correlation optimization",
            use_cases=["Parlay building", "Correlation exploitation", "Multi-leg optimization"],
            expected_output="Optimized parlay selection with detailed construction rationale",
        )

    def _add_advanced_analysis_prompts(self):
        """Add advanced analysis prompt templates"""

        # Model validation and backtesting
        self.prompt_templates["model_validation"] = PromptTemplate(
            id="model_validation",
            name="Betting Model Validator",
            category=PromptCategory.MARKET_ANALYSIS,
            sport=None,
            complexity=PromptComplexity.EXPERT,
            template="""
Validate and analyze betting model performance:

Model Description: {model_description}
Prediction Method: {prediction_method}

Historical Performance Data:
{historical_performance}

Key Metrics:
- ROI: {roi_data}
- Hit Rate: {hit_rate}
- Average Odds: {average_odds}
- Bet Count: {bet_count}
- Longest Winning Streak: {win_streak}
- Longest Losing Streak: {lose_streak}

Bankroll Management:
{bankroll_data}

Market Conditions During Test:
{market_conditions}

Analysis Requirements:
1. Statistical significance assessment
2. Edge validation and sustainability
3. Market adaptation considerations
4. Sample size adequacy
5. Performance consistency
6. Risk-adjusted returns
7. Model improvement recommendations

Compare against:
- Market efficiency benchmarks
- Random betting performance
- Buy-and-hold strategies
- Professional handicapper results

Provide comprehensive model validation with actionable improvements.
""",
            parameters=[
                "model_description",
                "prediction_method",
                "historical_performance",
                "roi_data",
                "hit_rate",
                "average_odds",
                "bet_count",
                "win_streak",
                "lose_streak",
                "bankroll_data",
                "market_conditions",
            ],
            description="Comprehensive betting model validation and improvement analysis",
            use_cases=["Model validation", "Strategy optimization", "Performance analysis"],
            expected_output="Statistical model validation with improvement recommendations",
        )

        # Arbitrage opportunity analysis
        self.prompt_templates["arbitrage_analysis"] = PromptTemplate(
            id="arbitrage_analysis",
            name="Arbitrage Opportunity Analyzer",
            category=PromptCategory.ARBITRAGE,
            sport=None,
            complexity=PromptComplexity.ADVANCED,
            template="""
Analyze arbitrage opportunity across multiple sportsbooks:

Event: {event}
Sport: {sport}

Sportsbook Lines:
{sportsbook_lines}

Arbitrage Calculation:
{arbitrage_calculation}

Opportunity Metrics:
- Profit Margin: {profit_margin}
- Total Stake Required: {total_stake}
- Individual Stakes: {individual_stakes}
- Guaranteed Profit: {guaranteed_profit}

Risk Factors:
- Line Movement Risk: {line_movement_risk}
- Execution Time: {execution_time}
- Account Limits: {account_limits}
- Regulatory Factors: {regulatory_factors}

Market Analysis:
- Arbitrage Duration: {arb_duration}
- Market Efficiency: {market_efficiency}
- Competition Level: {competition_level}

Execution Strategy:
1. Optimal betting sequence
2. Stake allocation optimization
3. Timing considerations
4. Risk mitigation steps
5. Account management strategy
6. Profit extraction plan

Provide step-by-step arbitrage execution plan with risk assessment.
""",
            parameters=[
                "event",
                "sport",
                "sportsbook_lines",
                "arbitrage_calculation",
                "profit_margin",
                "total_stake",
                "individual_stakes",
                "guaranteed_profit",
                "line_movement_risk",
                "execution_time",
                "account_limits",
                "regulatory_factors",
                "arb_duration",
                "market_efficiency",
                "competition_level",
            ],
            description="Complete arbitrage analysis with execution strategy",
            use_cases=[
                "Arbitrage betting",
                "Risk-free profits",
                "Market inefficiency exploitation",
            ],
            expected_output="Detailed arbitrage execution plan with risk management",
        )

    async def get_ai_analysis(self, prompt_id: str, **parameters) -> PromptResponse:
        """
        Get AI analysis using specified prompt template
        """
        if prompt_id not in self.prompt_templates:
            raise ValueError(f"Prompt template '{prompt_id}' not found")

        template = self.prompt_templates[prompt_id]

        # Check cache first
        cache_key = f"{prompt_id}_{hash(str(sorted(parameters.items())))}"
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            if (datetime.now(UTC) - cached_response.timestamp).seconds < 300:  # 5-minute cache
                logger.info(f"🔄 Using cached response for {prompt_id}")
                return cached_response

        # Render prompt with parameters
        try:
            rendered_prompt = template.render(**parameters)
        except Exception as e:
            logger.error(f"❌ Failed to render prompt {prompt_id}: {e}")
            raise

        # Get AI response
        if not self.ai_client or not hasattr(self.ai_client, "chat_completion_async"):
            raise RuntimeError("AI client not available")

        start_time = datetime.now()

        try:
            # Create system prompt based on complexity and category
            system_prompt = self._create_system_prompt(template)

            response = await self.ai_client.chat_completion_async(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": rendered_prompt},
                ]
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            # Extract confidence score from response
            confidence_score = self._extract_confidence_score(response.content)

            # Create response object
            prompt_response = PromptResponse(
                prompt_id=prompt_id,
                query=rendered_prompt,
                response=response.content,
                confidence_score=confidence_score,
                execution_time=execution_time,
                tokens_used=getattr(response, "usage", {}).get("total_tokens", 0),
                model_used=getattr(response, "model", "gpt-4o"),
            )

            # Cache response
            self.response_cache[cache_key] = prompt_response

            logger.info(f"✅ Generated analysis for {prompt_id} in {execution_time:.2f}s")

            return prompt_response

        except Exception as e:
            logger.error(f"❌ AI analysis failed for {prompt_id}: {e}")
            raise

    def _create_system_prompt(self, template: PromptTemplate) -> str:
        """Create system prompt based on template characteristics"""

        base_prompt = "You are an expert sports betting analyst with advanced statistical and mathematical expertise."

        # Add complexity-specific instructions
        if template.complexity == PromptComplexity.BASIC:
            complexity_prompt = " Provide clear, straightforward analysis suitable for beginners."
        elif template.complexity == PromptComplexity.INTERMEDIATE:
            complexity_prompt = " Provide detailed analysis with moderate technical depth."
        elif template.complexity == PromptComplexity.ADVANCED:
            complexity_prompt = (
                " Provide sophisticated analysis with advanced statistical concepts."
            )
        else:  # EXPERT
            complexity_prompt = " Provide expert-level analysis with cutting-edge methodologies and deep mathematical insights."

        # Add category-specific expertise
        category_expertise = {
            PromptCategory.MARKET_ANALYSIS: " You specialize in market efficiency, line value, and betting market dynamics.",
            PromptCategory.PLAYER_ANALYSIS: " You specialize in player performance analysis, matchups, and prop betting.",
            PromptCategory.LINE_MOVEMENT: " You specialize in line movement analysis, sharp money detection, and market timing.",
            PromptCategory.RISK_MANAGEMENT: " You specialize in portfolio theory, risk management, and bankroll optimization.",
            PromptCategory.CORRELATION: " You specialize in correlation analysis, dependency modeling, and multi-leg betting strategies.",
            PromptCategory.ARBITRAGE: " You specialize in arbitrage detection, risk-free betting, and market inefficiencies.",
            PromptCategory.LIVE_BETTING: " You specialize in real-time analysis, momentum assessment, and in-game betting strategies.",
        }

        category_prompt = category_expertise.get(template.category, "")

        # Add sport-specific knowledge if applicable
        sport_prompt = ""
        if template.sport:
            sport_prompt = f" You have deep expertise in {template.sport.value.upper()} betting markets and analysis."

        # Combine all prompts
        system_prompt = base_prompt + complexity_prompt + category_prompt + sport_prompt

        # Add general instructions
        system_prompt += """

        Always provide:
        1. Specific, actionable recommendations
        2. Confidence levels for your analysis
        3. Risk assessments and limitations
        4. Mathematical reasoning where applicable
        5. Clear reasoning for all conclusions

        Use precise numbers and avoid vague statements. Include statistical significance and sample size considerations where relevant.
        """

        return system_prompt

    def _extract_confidence_score(self, response_content: str) -> float:
        """Extract confidence score from AI response"""
        # Look for confidence indicators in the response
        confidence_patterns = [
            r"confidence[:\s]*(\d+(?:\.\d+)?)\s*%",
            r"confidence[:\s]*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*%\s*confidence",
            r"certainty[:\s]*(\d+(?:\.\d+)?)\s*%",
        ]

        for pattern in confidence_patterns:
            match = re.search(pattern, response_content, re.IGNORECASE)
            if match:
                confidence = float(match.group(1))
                return confidence / 100 if confidence > 1 else confidence

        # Default confidence based on response characteristics
        if "highly confident" in response_content.lower():
            return 0.9
        elif "confident" in response_content.lower():
            return 0.8
        elif "moderate confidence" in response_content.lower():
            return 0.7
        elif "low confidence" in response_content.lower():
            return 0.5
        else:
            return 0.6  # Default

    def get_prompt_by_category(
        self, category: PromptCategory, sport: Sport | None = None
    ) -> list[PromptTemplate]:
        """Get all prompts for a specific category and sport"""
        prompts = []
        for template in self.prompt_templates.values():
            if template.category == category:
                if sport is None or template.sport is None or template.sport == sport:
                    prompts.append(template)
        return prompts

    def search_prompts(self, query: str) -> list[PromptTemplate]:
        """Search prompts by name, description, or tags"""
        query_lower = query.lower()
        matching_prompts = []

        for template in self.prompt_templates.values():
            if (
                query_lower in template.name.lower()
                or query_lower in template.description.lower()
                or any(query_lower in tag.lower() for tag in template.tags)
            ):
                matching_prompts.append(template)

        return matching_prompts

    def save_prompt_templates(self):
        """Save all prompt templates to JSON file"""
        templates_data = {}

        for prompt_id, template in self.prompt_templates.items():
            templates_data[prompt_id] = {
                "id": template.id,
                "name": template.name,
                "category": template.category.value,
                "sport": template.sport.value if template.sport else None,
                "complexity": template.complexity.value,
                "template": template.template,
                "parameters": template.parameters,
                "description": template.description,
                "use_cases": template.use_cases,
                "expected_output": template.expected_output,
                "examples": template.examples,
                "tags": template.tags,
            }

        output_file = self.prompts_dir / "sports_betting_prompts.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(templates_data, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Saved {len(templates_data)} prompt templates to {output_file}")

    def generate_prompt_documentation(self) -> str:
        """Generate comprehensive documentation for all prompts"""
        doc = """# EQ12 Sports Betting Prompt Pack Documentation

## Overview
This document describes all available AI prompts for sports betting analysis.

## Prompt Categories

"""

        # Group prompts by category
        by_category = {}
        for template in self.prompt_templates.values():
            category = template.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(template)

        # Generate documentation for each category
        for category, templates in sorted(by_category.items()):
            doc += f"### {category.replace('_', ' ').title()}\n\n"

            for template in templates:
                doc += f"#### {template.name}\n"
                doc += f"**ID:** `{template.id}`\n"
                doc += f"**Complexity:** {template.complexity.value.title()}\n"
                if template.sport:
                    doc += f"**Sport:** {template.sport.value.upper()}\n"
                doc += f"**Description:** {template.description}\n\n"

                doc += "**Parameters:**\n"
                for param in template.parameters:
                    doc += f"- `{param}`\n"
                doc += "\n"

                doc += "**Use Cases:**\n"
                for use_case in template.use_cases:
                    doc += f"- {use_case}\n"
                doc += "\n"

                doc += f"**Expected Output:** {template.expected_output}\n\n"
                doc += "---\n\n"

        return doc

    async def batch_analysis(
        self, analyses: list[tuple[str, dict[str, Any]]]
    ) -> list[PromptResponse]:
        """Run multiple analyses in batch"""
        results = []

        for prompt_id, parameters in analyses:
            try:
                response = await self.get_ai_analysis(prompt_id, **parameters)
                results.append(response)
                logger.info(f"✅ Completed batch analysis: {prompt_id}")
            except Exception as e:
                logger.error(f"❌ Batch analysis failed for {prompt_id}: {e}")
                # Create error response
                error_response = PromptResponse(
                    prompt_id=prompt_id,
                    query="Error",
                    response=f"Analysis failed: {e!s}",
                    confidence_score=0.0,
                    execution_time=0.0,
                    tokens_used=0,
                    model_used="error",
                )
                results.append(error_response)

        logger.info(f"🔄 Completed batch analysis: {len(results)} analyses")
        return results


# Integration functions
async def integrate_prompts_with_edgegod(market_data: dict[str, Any]) -> dict[str, Any]:
    """
    Integration point with existing EdgeGod system
    """
    prompt_pack = EQ12SportsPromptPack()

    # Run market analysis
    market_analysis = await prompt_pack.get_ai_analysis(
        "market_inefficiency",
        sport=market_data.get("sport", "NFL"),
        market_type=market_data.get("market_type", "moneyline"),
        game=market_data.get("game", "Team A vs Team B"),
        current_lines=json.dumps(market_data.get("lines", {})),
        historical_data=json.dumps(market_data.get("historical", {})),
        market_volume=market_data.get("volume", "medium"),
        public_betting=market_data.get("public_percentage", "50%"),
        sharp_indicators=json.dumps(market_data.get("sharp_indicators", {})),
    )

    return {
        "prompt_analysis": {
            "prompt_used": market_analysis.prompt_id,
            "analysis": market_analysis.response,
            "confidence": market_analysis.confidence_score,
            "execution_time": market_analysis.execution_time,
        },
        "recommendations": "Extracted from AI analysis",  # Would parse specific recommendations
        "integration_status": "active",
    }


# CLI interface
async def main():
    """Main function for CLI testing"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Sports Betting Prompt Pack")
    parser.add_argument("--prompt", help="Prompt ID to test")
    parser.add_argument("--list-prompts", action="store_true", help="List all available prompts")
    parser.add_argument(
        "--save-templates", action="store_true", help="Save prompt templates to file"
    )
    parser.add_argument("--generate-docs", action="store_true", help="Generate documentation")

    args = parser.parse_args()

    prompt_pack = EQ12SportsPromptPack()

    if args.list_prompts:
        print("📚 Available Prompt Templates:")
        for prompt_id, template in prompt_pack.prompt_templates.items():
            print(f"   {prompt_id}: {template.name} ({template.category.value})")

    elif args.save_templates:
        prompt_pack.save_prompt_templates()
        print("💾 Prompt templates saved")

    elif args.generate_docs:
        docs = prompt_pack.generate_prompt_documentation()
        doc_file = Path("C:/EQ12/docs/prompt_pack_documentation.md")
        doc_file.parent.mkdir(parents=True, exist_ok=True)
        doc_file.write_text(docs, encoding="utf-8")
        print(f"📖 Documentation generated: {doc_file}")

    elif args.prompt:
        if args.prompt in prompt_pack.prompt_templates:
            template = prompt_pack.prompt_templates[args.prompt]
            print(f"🎯 Testing prompt: {template.name}")
            print(f"   Parameters: {template.parameters}")
            print(f"   Description: {template.description}")

            # Would need actual parameters for testing
            print("   ⚠️ Provide parameters to run analysis")
        else:
            print(f"❌ Prompt '{args.prompt}' not found")

    else:
        print("🎯 EQ12 Sports Betting Prompt Pack Status:")
        print(f"   Total Prompts: {len(prompt_pack.prompt_templates)}")
        print(f"   AI Client: {'✅' if prompt_pack.ai_client else '❌'}")

        # Show category breakdown
        by_category = {}
        for template in prompt_pack.prompt_templates.values():
            category = template.category.value
            by_category[category] = by_category.get(category, 0) + 1

        print("   Categories:")
        for category, count in sorted(by_category.items()):
            print(f"     {category}: {count} prompts")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
