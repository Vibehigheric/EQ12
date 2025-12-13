# EQ12 User Task Templates
## Version: 1.0 | Last Updated: 2025-10-05

## TASK TYPE 1: PARLAY BUILDER

### Template: Basic Parlay Construction
```
Build {num_parlays} parlays with max {max_legs} legs each.
Minimum EV: {min_ev_percent}%
Bankroll: ${bankroll}
Kelly cap per leg: {kelly_cap}%
Strategy preference: {strategy}

Odds data: {odds_json_blob}
```

### Example Usage
```
Build 3 parlays with max 4 legs each.
Minimum EV: 3%  
Bankroll: $1000
Kelly cap per leg: 2%
Strategy preference: hook_spread

Odds data: [attached JSON file]
```

### Template: Live Game Focus
```
Build parlays for games starting within {time_window} hours.
Steam detection mode: {enabled/disabled}
Books priority: {book_preference_order}
Correlation filter: {strict/medium/loose}

Current slate: {games_list}
```

## TASK TYPE 2: ODDS EXTRACTION & NORMALIZATION

### Template: Raw Data Processing
```
Extract DK/FD/BM odds from this blob into normalized JSON.
Required markets: {market_list}
Time format: UTC RFC3339 only
Drop any data from excluded books.

Raw input: {raw_odds_blob}
```

### Template: Freshness Validation  
```
Validate freshness of attached odds data.
Stale threshold: {minutes} minutes
Flag any games with missing books.
Return extraction summary with warnings.

Data blob: {odds_json}
```

## TASK TYPE 3: VALUE HUNTING

### Template: Hook Number Focus
```
Find value opportunities on hook spreads/totals.
Target books: {book_list}
Hook priority: 0.5, 3.0, 7.0, 14.0 point spreads
Minimum edge: {min_ev}%
Risk tolerance: {LOW/MEDIUM/HIGH}

Market scan: {odds_data}
```

### Template: Steam Detection
```
Identify rapid line movement in past {time_window} minutes.
Movement threshold: ≥{point_threshold} points or ≥{odds_threshold} odds change  
Books monitored: DraftKings, FanDuel, BetMGM
Alert on reverse line movement.

Historical snapshots: {time_series_data}
```

## TASK TYPE 4: PORTFOLIO ANALYSIS

### Template: Parlay Validation
```
Validate this parlay against EQ12 rules.
Check for: correlations, book mixing, stale data, EV thresholds
If violations found, suggest minimal corrections.
Return validation report + corrected version.

Parlay to validate: {parlay_json}
```

### Template: Risk Assessment
```  
Assess risk profile of attached betting portfolio.
Calculate: max drawdown, Kelly overbetting, correlation exposure
Bankroll: ${bankroll}
Risk tolerance: {conservative/moderate/aggressive}

Portfolio: {portfolio_json}
```

## TASK TYPE 5: MARKET ANALYSIS

### Template: Line Shopping
```
Compare lines across DK/FD/BM for {game_id}.
Identify: best odds per market, arbitrage opportunities, steam direction
Time sensitivity: {high/medium/low}
Market focus: {moneyline/spread/total/all}

Current lines: {multi_book_odds}
```

### Template: Closing Line Value  
```
Calculate CLV for completed bets vs closing lines.
Time period: {start_date} to {end_date}
Minimum sample size: {min_bets} bets
Group by: book, market type, strategy

Bet history: {historical_bets}
Closing lines: {closing_odds_data}
```

## TASK TYPE 6: CONFIGURATION & SETUP

### Template: Model Calibration
```
Calibrate probability model for NFL {week_type}.
Historical accuracy target: {target_percentage}%
Adjust for: home field advantage, weather, injuries, public bias
Sample period: {date_range}

Performance data: {model_results}
```

### Template: Bankroll Management
```
Set optimal Kelly fractions for current bankroll.
Bankroll: ${amount}
Growth target: {percentage}% per season
Max drawdown tolerance: {percentage}%  
Betting frequency: {daily/weekly}

Risk parameters: {risk_config}
```

## QUICK REFERENCE CONFIGS

### Minimum Viable Task
```
Build 1 parlay, max 3 legs, min 2% EV.
Bankroll: $500, Kelly cap: 1.5%.
Use attached odds, prefer DraftKings.
```

### Production Daily Task
```
Build 5 parlays from today's NFL slate.
Max legs: 8, min EV: 3%, bankroll: $2000.
Strategy mix: 60% hook_spread, 40% value_hunt.
Steam detection: enabled.
Books: DK primary, FD secondary, BM tertiary.
```

### Emergency/Stale Data Task
```
Extract best available opportunities from 30+ minute old odds.
Flag all uncertain data, increase risk ratings.
Minimum EV: 5% (higher threshold for stale data).
Maximum 2 legs per parlay (reduce correlation risk).
```

## RESPONSE EXPECTATIONS

### What User Gets Back
- Valid JSON matching schema (no prose)
- All required fields populated  
- Risk flags and freshness warnings
- Brief justification per selection (≤20 words)
- Clear notes on any data issues

### What User Should NOT Expect
- Financial advice or guarantees
- Chain-of-thought explanations  
- Predictions beyond probability estimates
- Support for non-DK/FD/BM books
- Correlation-heavy parlays (>1 leg per game)