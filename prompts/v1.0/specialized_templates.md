# EQ12 Specialized Prompt Templates
## Version: 1.0 | Last Updated: 2025-10-05

## EXTRACTOR TEMPLATE

### Raw Odds Normalization
```
GOAL: Extract DK/FD/BM odds only into normalized JSON schema.

INPUT: {raw_odds_blob}

REQUIREMENTS:
- Only include draftkings, fanduel, betmgm data
- Convert all timestamps to UTC RFC3339 format  
- Drop any other bookmakers (Caesars, ESPN, etc.)
- Normalize team names to lowercase
- Game IDs format: nfl_YYYYMMDD_away_home

OUTPUT: Valid JSON matching odds_extract_schema.json
- No prose, explanations, or markdown
- Include stale_data_warning if any odds >15min old
- List missing_books if DK/FD/BM data unavailable

EXAMPLE OUTPUT:
{
  "extracted_at_utc": "2025-10-05T19:30:00Z",
  "games": [...],
  "stale_data_warning": false,
  "missing_books": []
}
```

### Log File Analysis
```
GOAL: Extract betting opportunities from EQ12 log files.

INPUT: {log_file_content}

FOCUS: Look for:
- API responses with odds data
- Steam detection alerts  
- Value hunting results
- Parlay builder outputs
- Error conditions requiring attention

FILTER: Events from last {time_window} hours only

OUTPUT: Structured summary with:
- opportunities_found: count
- steam_alerts: list of games with movement
- errors_detected: list of issues
- recommendations: next actions needed

NO PROSE: JSON only matching log analysis schema.
```

## VALIDATOR TEMPLATE

### Parlay Validation & Repair
```
GOAL: Validate parlay against EQ12 rules; fix minimally if violations found.

INPUT PARLAY: {parlay_json}

VALIDATION CHECKLIST:
☐ Book ∈ {draftkings, fanduel, betmgm}
☐ One leg per game (unique game_id values)
☐ UTC timestamps valid RFC3339
☐ No correlation violations  
☐ EV meets minimum threshold
☐ Kelly fractions ≤ max cap
☐ Risk flags assigned appropriately
☐ JSON schema compliant

IF VIOLATIONS FOUND:
- Fix automatically where possible
- Document changes in "corrections" array
- Upgrade risk flags if data uncertain
- Preserve user intent while enforcing rules

OUTPUT: validation_schema.json format
- validation_status: PASS/FAIL_CORRECTABLE/FAIL_UNCORRECTABLE
- violations_found: detailed list
- corrected_parlay: fixed version or null
- recommendations: suggested actions

NO CHAIN-OF-THOUGHT: Return JSON only.
```

### Portfolio Risk Assessment
```
GOAL: Analyze risk profile of betting portfolio.

INPUT: 
- portfolio: {portfolio_json}
- bankroll: ${bankroll_amount}
- risk_tolerance: {conservative/moderate/aggressive}

RISK DIMENSIONS:
- Correlation exposure (same games, divisions, weather)
- Kelly overbetting detection
- Concentration risk (single book dependency)
- Liquidity risk (market depth concerns)
- Recency bias (too many recent games)

CALCULATIONS:
- Max potential loss (worst case scenario)
- Expected portfolio volatility
- Sharpe ratio estimate
- Drawdown potential at 5th percentile

OUTPUT: Risk report with:
- overall_risk_score: 0-100
- risk_breakdown: by dimension
- position_sizing_alerts: if oversized
- diversification_suggestions: specific actions
- stress_test_results: scenario analysis

CONSTRAINTS: Conservative advice, err toward safety.
```

## SUMMARIZER TEMPLATE

### Human-Readable Parlay Summary
```
GOAL: Convert parlay JSON into concise bullet points for human review.

INPUT: {parlay_json}

OUTPUT FORMAT: Exactly 5 bullet points, ≤80 words total
• Strategy: {strategy_name} on {book}
• Risk: {overall_risk} with {confidence_level} confidence  
• Biggest Edge: {best_leg} (+{ev_percent}% EV because {brief_reason})
• Stake: ${stake_amount} (Kelly-sized, max loss ${max_loss})
• Timing: {num_legs} legs from {earliest_time} to {latest_time}

TONE: Factual, concise, no hype language
FOCUS: Key decision factors, not play-by-play
ALERTS: Flag any HIGH risk or stale data prominently
```

### Daily Performance Report  
```
GOAL: Summarize day's betting activity and outcomes.

INPUT:
- completed_bets: {bet_history}
- pending_bets: {active_positions}  
- bankroll_change: {daily_pnl}
- clv_data: {closing_line_value}

SECTIONS:
1. Performance Summary (W-L, ROI, CLV)
2. Best/Worst Decisions (highest +EV/worst -EV)
3. Market Insights (which books, strategies worked)
4. Risk Management (Kelly adherence, correlation exposure)
5. Tomorrow's Focus (opportunities, adjustments needed)

LENGTH: 150 words maximum
TONE: Analytical, forward-looking
METRICS: Include specific numbers, percentages
```

## CRITIQUE & REPAIR TEMPLATE

### Prompt Debugging Assistant
```
GOAL: Diagnose why a prompt isn't producing expected outputs.

INPUT: 
- prompt_text: {full_prompt}
- expected_output: {desired_behavior}
- actual_output: {what_model_returned}  
- failure_pattern: {consistency_issues}

ANALYSIS FRAMEWORK:
1. Instruction Clarity (ambiguous language?)
2. Schema Conflicts (competing requirements?)
3. Context Length (information overload?)
4. Example Quality (misleading demonstrations?)
5. Constraint Conflicts (impossible requirements?)

FIXES SUGGESTED:
- Minimal edits to improve clarity
- Constraint prioritization 
- Example improvements
- Schema simplifications
- Temperature/parameter adjustments

OUTPUT: Structured diagnosis with specific edit recommendations.
PRIORITY: Surgical fixes over complete rewrites.
```

### Output Quality Inspector
```
GOAL: Grade model output against EQ12 quality standards.

INPUT: {model_response}

QUALITY DIMENSIONS:
- Schema Compliance (0-100%)
- Policy Adherence (0-100%) 
- Math Accuracy (0-100%)
- Safety Standards (0-100%)
- User Experience (0-100%)

GRADING RUBRIC:
A: 95-100% (production ready)
B: 85-94% (minor issues)  
C: 70-84% (needs improvement)
D: 50-69% (significant problems)
F: <50% (unacceptable)

OUTPUT:
- overall_grade: A/B/C/D/F
- dimension_scores: detailed breakdown
- critical_issues: must-fix problems
- improvement_areas: enhancement opportunities
- deployment_recommendation: ready/needs_work/reject

STANDARDS: EQ12 production requirements, zero tolerance for safety violations.
```

## CONFIGURATION TEMPLATES

### Model Parameter Optimizer
```
GOAL: Recommend optimal model parameters for EQ12 prompts.

CONSIDERATIONS:
- Task type (extraction/analysis/validation)
- Consistency requirements (schema compliance)
- Creativity needs (strategy generation)
- Speed requirements (real-time/batch)
- Cost constraints (token usage)

RECOMMENDATIONS:
- Temperature: 0.1-0.3 for data tasks, 0.5-0.7 for strategy
- Max tokens: Conservative estimates with buffer
- Top-p: 0.9 for most tasks
- Frequency penalty: 0.0 (avoid repetition filtering)
- Presence penalty: 0.0 (maintain consistent terminology)

OUTPUT: Parameter config with reasoning for each setting.
```

### Prompt Version Controller  
```
GOAL: Track prompt changes and performance impact.

INPUT:
- prompt_v1: {baseline_version}
- prompt_v2: {modified_version} 
- performance_data: {A/B_test_results}

CHANGE ANALYSIS:
- Diff highlight (specific modifications)
- Performance delta (better/worse/neutral)
- Risk assessment (breaking changes?)
- Rollback recommendation (revert if degraded)

VERSIONING STRATEGY:
- Semantic versioning (major.minor.patch)
- Backward compatibility checks
- Staged rollout recommendations
- Performance monitoring requirements

OUTPUT: Change control report with deployment decision.
```

## USAGE GUIDELINES

### When to Use Each Template
- **Extractor**: Raw data processing, log analysis
- **Validator**: Quality control, compliance checking  
- **Summarizer**: Human communication, reporting
- **Critique**: Prompt debugging, quality assessment
- **Configuration**: System optimization, deployment

### Template Customization
- Replace {placeholders} with actual values
- Adjust constraints based on specific use case
- Maintain EQ12 core principles in all modifications
- Test template changes against eval suite

### Integration Points
- Use with EQ12 API client for live data
- Connect to scheduler for automated processing  
- Link to logging system for audit trails
- Interface with validation pipeline for quality gates