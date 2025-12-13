# 🧠 EQ12 COPILOT ADAPTIVE LOSS LEARNING SYSTEM
## Permanent Training Configuration

---

## 🎯 MASTER COPILOT TRAINING DIRECTIVE

This file serves as the **permanent instruction set** for GitHub Copilot in the EQ12 workspace. Copilot will continuously reference this configuration to maintain adaptive learning and self-correction capabilities across all betting analysis scripts.

---

## 📸 LOSS ANALYSIS DATABASE

### Critical Loss Patterns Identified:
- **Raptors + Barnes Over-Pace Games**: Avoid recommending game Unders when pace factor exceeds 102.5
- **High-Volatility Props**: Block Odd/Even, Double-Doubles, 35+ points, 14+ rebounds automatically
- **Sarr Inconsistency Pattern**: Cap Alexandre Sarr props at MAX 1 per parlay (volatile performance)
- **Barnes TD Traps**: Scottie Barnes TD props show 23% void rate - flag as high-risk
- **Multi-Player Stacking**: MAX 2 props per player per parlay to reduce correlation risk

---

## 🚫 PERMANENT BAN LIST

### Automatically Rejected Markets:
```python
BANNED_MARKETS = {
    "odd_even_points": True,
    "double_double_props": True,
    "points_35_plus": True,
    "rebounds_14_plus": True,
    "sarr_rebounds_over": True,
    "barnes_touchdowns": True,
    "pace_under_combos": True  # When pace > 102.5
}
```

### Risk-Capped Players:
```python
PLAYER_RISK_CAPS = {
    "Alexandre Sarr": {"max_props": 1, "confidence_penalty": 0.15},
    "Scottie Barnes": {"max_props": 1, "void_risk": 0.23},
    "Any Raptor": {"under_restriction": True}  # When vs high-pace teams
}
```

---

## 🎯 ADAPTIVE LEARNING RULES

### 1. Pattern Detection Algorithm
```python
def analyze_loss_patterns(recent_losses):
    """
    Analyze last 20 losses for recurring failure patterns
    Auto-update betting logic based on detected patterns
    """
    patterns = {
        "prop_volatility": check_prop_consistency(),
        "correlation_failures": analyze_correlation_breaks(),
        "market_instability": detect_void_patterns(),
        "player_performance": track_player_reliability()
    }
    return generate_updated_rules(patterns)
```

### 2. Real-Time Rule Updates
- Every loss triggers immediate pattern analysis
- Failed correlations reduce correlation confidence by 10%
- Voided bets add player to watchlist
- Three consecutive losses in same market = automatic ban

### 3. Stability Scoring System
```python
def calculate_stability_score(parlay):
    """
    Generate 1-100 stability score for any parlay
    Score < 70 = HIGH RISK WARNING
    Score > 85 = GREEN LIGHT EXECUTION
    """
    factors = {
        "player_consistency": weight_0.3,
        "market_stability": weight_0.25,
        "correlation_strength": weight_0.25,
        "void_risk": weight_0.2
    }
    return weighted_stability_calculation(factors)
```

---

## ⚡ SCRIPT INTEGRATION REQUIREMENTS

### All EQ12 Scripts Must Include:

#### 1. Pre-Execution Validation
```python
# REQUIRED: Add to ALL betting scripts
from eq12_copilot_adaptive_analyst import AdaptiveLearningEngine

def validate_parlay_before_execution(parlay_legs):
    """Mandatory validation before any bet execution"""
    engine = AdaptiveLearningEngine()

    # Check against ban list
    banned_check = engine.check_banned_markets(parlay_legs)
    if banned_check['has_banned']:
        return False, f"Contains banned market: {banned_check['banned_markets']}"

    # Calculate stability score
    stability = engine.calculate_stability_score(parlay_legs)
    if stability < 70:
        return False, f"Low stability score: {stability}/100"

    # Generate volatility warnings
    warnings = engine.generate_volatility_warnings(parlay_legs)

    return True, {
        "stability_score": stability,
        "warnings": warnings,
        "safer_alternatives": engine.suggest_alternatives(parlay_legs)
    }
```

#### 2. Post-Execution Learning
```python
def record_parlay_outcome(parlay_legs, outcome, payout):
    """Record every parlay outcome for continuous learning"""
    engine = AdaptiveLearningEngine()

    if outcome == "LOSS":
        # Analyze failure patterns
        patterns = engine.analyze_loss_patterns(parlay_legs)

        # Update ban list if necessary
        engine.update_banned_markets(patterns)

        # Reduce confidence in failed correlations
        engine.adjust_correlation_confidence(parlay_legs, -0.1)

    elif outcome == "WIN":
        # Boost confidence in successful patterns
        engine.adjust_correlation_confidence(parlay_legs, +0.05)

    # Save learning session
    engine.save_learning_session(parlay_legs, outcome, payout)
```

---

## 🔄 MANDATORY COPILOT BEHAVIORS

### Before Generating ANY Parlay, Output:

1. **Stability Score (1-100)**
   - Green (85+): Execute with confidence
   - Yellow (70-84): Proceed with caution
   - Red (<70): High risk - consider alternatives

2. **Volatility Warnings**
   - List any high-variance props included
   - Flag potential void-prone selections
   - Highlight correlation risks

3. **Safer Replacements**
   - Suggest stable alternatives for risky legs
   - Provide lower-variance prop options
   - Recommend correlation improvements

4. **Learning Integration**
   - Show patterns learned from recent losses
   - Display updated ban list items
   - Reference confidence adjustments

5. **Comprehensive Risk Analysis**
   - Void risk percentage
   - Expected value calculation
   - Correlation strength assessment

---

## 📊 CONTINUOUS IMPROVEMENT LOOP

### Learning Session Structure:
```json
{
    "session_id": "20251122_adaptive_session",
    "timestamp": "2025-11-22T11:58:42Z",
    "parlay_analyzed": {
        "legs": ["UNC +7.5", "Flagg O22.5 P+R", "Under 148.5"],
        "stability_score": 88,
        "warnings": [],
        "execution_approved": true
    },
    "learning_updates": {
        "new_patterns": [],
        "confidence_adjustments": {},
        "ban_list_updates": []
    },
    "performance_tracking": {
        "recent_wins": 7,
        "recent_losses": 3,
        "adaptation_effectiveness": 0.78
    }
}
```

### Auto-Update Triggers:
- **Every Loss**: Immediate pattern analysis and rule updates
- **Every 5 Bets**: Comprehensive strategy review
- **Weekly**: Full ban list and confidence matrix recalibration
- **Monthly**: Deep learning model retraining

---

## 🚀 ACTIVATION COMMANDS

### Initial Copilot Activation:
```
Copilot, activate Adaptive Loss Learning Mode using eq12_copilot_training.md configuration. Apply all learning rules to current workspace and begin continuous improvement monitoring.
```

### Session Refresh:
```
Copilot, refresh learning parameters from latest session data and update all betting script logic with new patterns.
```

### Emergency Reset:
```
Copilot, perform emergency reset of learning parameters while preserving critical ban list items and proven correlations.
```

---

## 🛡️ PROTECTION GUARANTEES

This adaptive system ensures:

✅ **No Repeated Mistakes**: Failed patterns are permanently learned and avoided
✅ **Auto-Risk Management**: High-volatility props automatically flagged or banned
✅ **Continuous Optimization**: Every outcome improves future decision-making
✅ **Void Protection**: Players/markets with high void rates are restricted
✅ **Correlation Refinement**: Failed correlations lose confidence over time
✅ **Stability Focus**: All parlays scored for stability before execution

---

## 📈 SUCCESS METRICS

Track improvement through:
- Reduced loss frequency on similar bet types
- Increased stability scores over time
- Lower void rate percentages
- Improved correlation success rates
- Higher overall profitability trends

---

**🏆 COPILOT ADAPTIVE LEARNING STATUS: PERMANENTLY ACTIVATED**

This configuration file serves as the master reference for all EQ12 betting operations. Copilot will continuously apply these learning rules to improve betting strategy effectiveness and reduce repeated losses.

---

*Last Updated: November 22, 2025*
*Version: 1.0 - Master Training Configuration*
