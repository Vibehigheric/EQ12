# EQ12 Model Response System - Complete Documentation

## Overview

The EQ12 Model Response System is a comprehensive integration of OpenAI's Responses API designed specifically for advanced sports betting analysis. It provides a complete toolkit for analyzing betting opportunities, managing portfolios, detecting market inefficiencies, and optimizing bet sizing using state-of-the-art AI capabilities.

## Architecture

The system consists of three main components:

### 1. Core Response Engine (`eq12_model_responses.py`)
- **Purpose**: Direct interface to OpenAI Responses API v1 endpoint
- **Features**: Full parameter support, tool integration, background processing
- **Key Classes**: `EQ12ResponsesAPI`, `ResponseConfig`, service tier management
- **Capabilities**: Streaming responses, conversation state, structured outputs

### 2. Pre-configured Templates (`eq12_response_templates.py`)
- **Purpose**: Optimized response templates for common betting scenarios
- **Features**: Sport-specific analysis, pre-tuned parameters, validated schemas
- **Key Classes**: `EQ12ResponseTemplates`, `BettingScenario`, scenario execution
- **Templates**: NFL slate, NBA props, live betting, steam detection, portfolio optimization

### 3. Unified Interface (`eq12_unified_responses.py`)
- **Purpose**: Single entry point for all response capabilities
- **Features**: Batch processing, session management, health monitoring
- **Key Classes**: `EQ12UnifiedResponseSystem`, convenience functions
- **Capabilities**: Multi-scenario analysis, live monitoring sessions, error handling

## Supported Betting Scenarios

### Parlay Analysis
```python
# Comprehensive parlay evaluation with correlation analysis
await analyze_parlay_with_responses(
    game_details="NBA games tonight",
    legs=[
        {"game": "Lakers vs Warriors", "selection": "Lakers -3.5", "odds": -110},
        {"game": "Lakers vs Warriors", "selection": "Over 225.5", "odds": -105}
    ],
    bankroll=5000.0
)
```

**Analysis Includes**:
- Expected value calculation for each leg and overall parlay
- Correlation analysis between legs (positive/negative dependencies)
- Kelly Criterion optimal bet sizing recommendations
- Risk assessment with worst-case scenarios
- Alternative leg suggestions for improved value
- Market intelligence across multiple sportsbooks

### NFL Sunday Slate Analysis
```python
# Complete slate analysis with weather, injuries, and correlations
await analyze_nfl_sunday_slate(
    games=[
        {"home": "Patriots", "away": "Bills", "spread": "Bills -3.5"},
        {"home": "Cowboys", "away": "Eagles", "spread": "Eagles -7"}
    ],
    weather=[{"game": "Patriots vs Bills", "wind": "15mph", "temp": "28°F"}],
    injuries=[{"player": "Josh Allen", "status": "Questionable", "impact": "High"}],
    bankroll=10000.0
)
```

**Analysis Includes**:
- Weather impact assessment on totals and spreads
- Late-breaking injury news integration and line movement
- Public vs sharp money identification
- Game correlation opportunities and stack construction
- Divisional rivalry and historical trend factors
- Optimal bankroll allocation across 16+ game slate

### NBA Player Props
```python
# Advanced player prop analysis with usage rates and matchups
await analyze_nba_props_night(
    games=[{"home": "Lakers", "away": "Warriors", "pace": 102.5}],
    props=[
        {"player": "LeBron James", "market": "points", "line": 26.5, "odds": -110},
        {"player": "Stephen Curry", "market": "threes", "line": 4.5, "odds": +105}
    ],
    injuries=[{"player": "Anthony Davis", "status": "Out", "replacement": "Christian Wood"}]
)
```

**Analysis Includes**:
- Usage rate changes with lineup variations
- Pace factor adjustments for totals
- Matchup advantages against specific defenders
- Load management and rest pattern tracking
- Injury chain analysis for teammate usage bumps
- Same-game parlay correlation opportunities

### Live Betting & Momentum Analysis
```python
# Real-time in-game analysis with momentum tracking
await templates.execute_scenario(
    BettingScenario.LIVE_GAME_MOMENTUM,
    {
        "game_state": {"score": "Lakers 68, Warriors 71", "time": "3rd Q 8:42"},
        "live_lines": {"spread": "Warriors -2.5", "total": 228.5},
        "momentum": ["Warriors 12-3 run", "LeBron 3 fouls", "Curry hot shooting"]
    }
)
```

**Analysis Includes**:
- Real-time win probability vs live odds discrepancies
- Momentum indicator tracking (runs, turnovers, foul trouble)
- Regression opportunity identification
- Optimal hedge and cash-out timing
- Clock management and game theory factors

### Sharp Steam Detection
```python
# Professional betting activity detection and following
await detect_steam_moves([
    {"game": "Patriots vs Bills", "market": "spread", "movement": 1.0, "public_pct": 35},
    {"game": "Cowboys vs Eagles", "market": "total", "movement": -1.5, "volume_spike": True}
])
```

**Analysis Includes**:
- Reverse line movement identification
- Volume spike and timing pattern analysis
- Sportsbook behavior monitoring (limits, line pulls)
- Closing line value prediction
- Professional betting window identification
- Follow strategy recommendations with sizing

### Portfolio Optimization
```python
# Kelly Criterion portfolio management with risk controls
await optimize_bankroll_kelly(
    bankroll=25000.0,
    positions=[{"id": "bet1", "stake": 500, "sport": "NFL", "correlation_group": "AFC_East"}],
    opportunities=[{"edge": 0.055, "odds": +150, "correlation_group": "NFC_West"}],
    risk_tolerance="moderate"
)
```

**Analysis Includes**:
- Kelly Criterion optimal bet sizing calculations
- Portfolio correlation and diversification analysis
- Dynamic position sizing based on recent performance
- Value-at-Risk and expected shortfall metrics
- Drawdown protection and rebalancing strategies
- Monte Carlo simulation for risk assessment

## Advanced Features

### Background Processing
```python
# Long-running analysis with status tracking
config = ResponseConfig(background=True, service_tier=ServiceTier.PRIORITY)
response = await api.create_parlay_analysis_response(
    game_details, legs, bankroll, config
)

# Check status later
status = await api.get_response_status(response["id"])
```

### Streaming Responses
```python
# Real-time streaming for live betting scenarios
config = ResponseConfig(stream=True, background=False)
stream_response = await api.create_live_odds_analysis_response(
    games=["Patriots vs Bills"],
    config=config
)
```

### Tool Integration

**Web Search**: Real-time odds, injury updates, weather data
```python
tools=[ToolType.WEB_SEARCH]  # Searches ESPN, DraftKings, FanDuel, Covers
```

**Code Interpreter**: Statistical modeling, Monte Carlo simulation
```python
tools=[ToolType.CODE_INTERPRETER]  # Advanced mathematical analysis
```

**Custom Functions**: EQ12-specific betting calculations
```python
tools=[ToolType.FUNCTION]  # calculate_parlay_odds, get_live_odds, analyze_player_stats
```

### Conversation Management
```python
# Multi-turn conversations with state persistence
conversation_id = "parlay_session_123"

# First analysis
initial = await api.create_parlay_analysis_response(
    game_details, legs, bankroll, conversation_id=conversation_id
)

# Follow-up with refinements
followup = await api.create_parlay_analysis_response(
    "Adjust analysis based on late injury news",
    updated_legs, bankroll, conversation_id=conversation_id
)
```

## Usage Examples

### Quick Analysis Functions
```python
from eq12_unified_responses import (
    quick_parlay_analysis,
    quick_nfl_slate_analysis,
    quick_steam_detection
)

# Immediate parlay analysis
result = await quick_parlay_analysis(legs, bankroll=2000.0)

# NFL slate with correlations
slate_result = await quick_nfl_slate_analysis(games, bankroll=5000.0)

# Steam move detection
steam_result = await quick_steam_detection(line_movements)
```

### Batch Processing
```python
# Analyze multiple opportunities in parallel
system = EQ12UnifiedResponseSystem()

opportunities = [
    {"type": "parlay", "data": {"legs": parlay_legs}},
    {"type": "nfl_slate", "data": {"games": nfl_games}},
    {"type": "steam_detection", "data": {"line_movements": movements}}
]

results = await system.batch_analyze_opportunities(opportunities, bankroll=10000.0)
```

### Live Monitoring Sessions
```python
# Start background monitoring with streaming updates
session_id = await system.start_live_monitoring_session([
    "Patriots vs Bills",
    "Cowboys vs Eagles"
])

# Check session status
status = await system.get_session_status(session_id)

# Stop when done
system.stop_session(session_id)
```

## Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...

# Optional configuration
EQ12_DEFAULT_MODEL=gpt-4o                    # Default model for analysis
EQ12_ENABLE_BACKGROUND=true                  # Enable background processing
EQ12_ENABLE_WEB_SEARCH=true                  # Enable web search tool
EQ12_ENABLE_FILE_SEARCH=true                 # Enable file search tool
EQ12_ENABLE_CODE_INTERPRETER=true            # Enable code interpreter
```

### Response Configuration
```python
config = ResponseConfig(
    model="gpt-4o",                    # Model selection
    temperature=0.1,                   # Lower = more deterministic
    max_output_tokens=4000,            # Response length limit
    max_tool_calls=10,                 # Tool usage limit
    background=False,                  # Background processing
    stream=True,                       # Streaming responses
    service_tier=ServiceTier.PRIORITY, # Processing priority
    parallel_tool_calls=True           # Concurrent tool execution
)
```

## Output Schemas

### Parlay Analysis Output
```json
{
  "parlay_analysis": {
    "overall_rating": "EXCELLENT|GOOD|FAIR|POOR|AVOID",
    "expected_value_pct": 5.2,
    "true_odds": 650,
    "sportsbook_odds": 600,
    "kelly_stake_pct": 2.1,
    "recommended_stake": 105.0,
    "max_loss_amount": 105.0,
    "correlation_factor": 0.85,
    "leg_analysis": [
      {
        "leg_description": "Lakers -3.5",
        "individual_ev_pct": 3.1,
        "confidence_level": "HIGH",
        "key_factors": ["Home court advantage", "Rest advantage"]
      }
    ],
    "risk_factors": ["Correlated legs increase variance"],
    "alternative_suggestions": ["Consider Lakers ML + Under for better value"],
    "reasoning": "Strong correlation between spread and total creates value opportunity"
  }
}
```

### NFL Slate Output
```json
{
  "nfl_slate_analysis": {
    "slate_overview": {
      "total_games": 16,
      "weather_concerns": ["Patriots/Bills wind 20mph"],
      "key_injuries": ["Josh Allen questionable"],
      "sharp_movement": ["Bills spread moved from -2.5 to -3.5"],
      "public_favorites": ["Cowboys, Chiefs, Bills"]
    },
    "top_plays": [
      {
        "game": "Patriots vs Bills",
        "play_type": "Under",
        "selection": "Under 44.5",
        "confidence": "HIGH",
        "edge_percentage": 7.2,
        "recommended_units": 2.0,
        "reasoning": "Wind 20mph + low temperature favors under"
      }
    ],
    "correlation_stacks": [
      {
        "stack_name": "AFC East Weather Under",
        "components": ["Patriots/Bills Under", "Jets/Dolphins Under"],
        "correlation_strength": 0.72,
        "expected_value": 8.5
      }
    ]
  }
}
```

### Live Analysis Output
```json
{
  "live_analysis": {
    "current_situation": {
      "game": "Lakers vs Warriors",
      "time_remaining": "3rd Q 8:42",
      "score": "Lakers 68, Warriors 71",
      "live_spread": "Warriors -2.5",
      "momentum_indicator": "Warriors Hot"
    },
    "immediate_opportunities": [
      {
        "market": "Lakers +2.5",
        "current_odds": +105,
        "fair_value": -110,
        "urgency": "HIGH",
        "max_stake": 200,
        "exit_strategy": "Hedge if Lakers take lead"
      }
    ],
    "hedge_alerts": ["Consider Lakers ML hedge on existing under bet"],
    "cash_out_recommendations": ["Cash out Warriors future at 75% value"]
  }
}
```

## Testing

### Unit Tests
```bash
# Run all unit tests
cd C:\EQ12
python -m pytest tests/test_eq12_model_responses.py -v

# Run specific test suites
python -m pytest tests/test_eq12_model_responses.py::TestEQ12ResponsesAPI -v
python -m pytest tests/test_eq12_model_responses.py::TestEQ12ResponseTemplates -v
python -m pytest tests/test_eq12_model_responses.py::TestEQ12UnifiedSystem -v
```

### Integration Tests
```bash
# Run integration tests (requires OPENAI_API_KEY)
python tests/test_eq12_model_responses.py integration
```

### Manual Testing
```python
# Test core functionality
from eq12_unified_responses import EQ12UnifiedResponseSystem

system = EQ12UnifiedResponseSystem()
health = await system.health_check()
print(f"System Status: {health['status']}")

# Test quick analysis
from eq12_unified_responses import quick_parlay_analysis
result = await quick_parlay_analysis(sample_legs, bankroll=1000.0)
```

## Error Handling

### API Errors
- Rate limit handling with exponential backoff
- Service tier fallback for overloaded priority queue
- Graceful degradation when tools unavailable
- Comprehensive error logging with request IDs

### Validation
- Input parameter validation before API calls
- Output schema validation for structured responses
- Conversation state integrity checks
- Bankroll and risk limit enforcement

### Monitoring
```python
# Health monitoring
health = await system.health_check()
status = system.get_system_status()

# Debug logging
# Check logs/eq12_responses.log for detailed debugging
# Check logs/responses_debug.jsonl for API call details
```

## Performance Optimization

### Caching
- Response caching for identical requests
- Conversation state persistence
- Tool result caching to reduce redundant calls

### Parallel Processing
- Concurrent tool execution when enabled
- Batch analysis with asyncio.gather
- Background processing for long-running analysis

### Resource Management
- Service tier selection based on urgency
- Token usage optimization with streaming
- Memory-efficient handling of large responses

## Security & Compliance

### API Key Management
- Environment variable storage only
- No hardcoded keys in source code
- Secure logging (API keys never logged)

### Data Privacy
- No sensitive betting data stored permanently
- Conversation state cleared on session end
- Debug logs exclude personal information

### Rate Limiting
- Automatic rate limit respect
- Exponential backoff on rate limit hits
- Service tier management for priority access

## Integration with EQ12 Ecosystem

### Budget Controls
- Integration with existing budget_enforcer
- Kelly Criterion sizing with bankroll limits
- Position size limits and stop-loss triggers

### Data Sources
- Real-time odds from multiple sportsbooks
- Weather data integration for outdoor sports
- Injury report monitoring and impact analysis

### Workflow Integration
- Seamless integration with existing EQ12 workflows
- PowerShell wrapper compatibility
- Dashboard integration for visualization

## Troubleshooting

### Common Issues

**No API Response**:
- Check OPENAI_API_KEY environment variable
- Verify internet connection
- Check API rate limits and billing

**Import Errors**:
- Ensure httpx installed: `pip install httpx`
- Verify pydantic installed: `pip install pydantic`
- Check Python version compatibility (3.8+)

**Invalid Responses**:
- Check model availability (gpt-4o, gpt-4o-mini)
- Verify request parameters match API specification
- Review logs/responses_debug.jsonl for details

**Performance Issues**:
- Use background processing for complex analysis
- Enable parallel tool calls for speed
- Select appropriate service tier

### Debug Mode
```python
import logging
logging.getLogger('eq12_model_responses').setLevel(logging.DEBUG)

# Enable detailed API logging
os.environ['EQ12_DEBUG'] = 'true'
```

## Future Enhancements

### Planned Features
- WebSocket streaming for real-time updates
- Machine learning model integration for edge detection
- Advanced portfolio optimization with options strategies
- Multi-sport correlation analysis
- Automated bet placement integration

### API Evolution
- Integration with new OpenAI Responses API features
- Enhanced tool capabilities as they become available
- Improved conversation management and memory
- Advanced structured output formats

---

*For support, check the EQ12 documentation at `AGENTS.md` or review test files for usage examples.*
