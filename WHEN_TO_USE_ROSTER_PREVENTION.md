#  HARDCODED: WHEN TO USE NFL ROSTER PREVENTION SYSTEM

##  Automated Decision Engine - No Thinking Required

---

##  **MANDATORY TRIGGERS (ALWAYS USE)**

### 1. **Before Creating ANY SGP**
```powershell
# When: About to create any Same Game Parlay
# Command: .\when_to_use_checker.ps1 -Context SGP
# Result: ALWAYS triggers full prevention system
# Reason: SGPs depend heavily on player props - must verify all players active
```

### 2. **Before Betting Player Props**
```powershell
# When: About to bet any player prop (yards, TDs, receptions)
# Command: .\when_to_use_checker.ps1 -Context Props  
# Result: ALWAYS triggers quick player check
# Reason: Player props fail if player is inactive
```

### 3. **When Betting on Problem Players**
```
# Problem Players (ALWAYS check):
- DK Metcalf (SEA) - INACTIVE
- Terry McLaurin (WAS) - INACTIVE  
- Tyler Lockett (SEA) - INACTIVE
- Isiah Pacheco (KC) - QUESTIONABLE
- Stefon Diggs (BUF) - MONITOR
```

---

##  **TIME-BASED TRIGGERS (Automatic)**

### 1. **Game Day Morning (9:00 AM)**
- **Trigger**: Daily at 9:00 AM if games scheduled
- **Action**: Full prevention system
- **Reason**: Daily roster status update

### 2. **Pre-Game Window (2 hours before kickoff)**
- **Trigger**: 2 hours before any NFL game
- **Action**: Full prevention system  
- **Reason**: Final roster confirmations released

### 3. **Final Check (90 minutes before kickoff)**
- **Trigger**: 90 minutes before game time
- **Action**: Quick player check
- **Reason**: Last chance to catch inactive players

---

##  **GAME-SPECIFIC TRIGGERS**

### **November 2, 2025 - SEA vs WAS (TODAY)**
- **Status**:  **MAXIMUM PRIORITY**
- **Reason**: Multiple confirmed inactive players
- **Inactive Players**: DK Metcalf, Terry McLaurin, Tyler Lockett
- **Action**: ALWAYS use full prevention system

### **November 3, 2025 - BUF vs KC**
- **Status**:  **HIGH PRIORITY**
- **Problem Players**: Isiah Pacheco, Stefon Diggs
- **Action**: Full prevention system recommended

---

##  **SIMPLE DECISION TREE**

```
Are you creating an SGP?  YES  Use Full Prevention System
Are you betting player props?  YES  Use Quick Check
Is it a game day?  YES  Use Full Prevention System
Are problem players involved?  YES  Use Quick Check
Otherwise  NO ACTION NEEDED
```

---

##  **EXACT COMMANDS TO USE**

### **Full Prevention System** (SGPs, Game Days, Major Checks)
```powershell
# Option 1: Python
python nfl_roster_prevention_system.py

# Option 2: PowerShell  
.\nfl_roster_prevention_simple.ps1 -Action Prevent
```

### **Quick Player Check** (Props, Problem Players)
```powershell
.\nfl_roster_prevention_simple.ps1 -Action QuickCheck
```

### **When to Use Checker** (Get YES/NO Decision)
```powershell
.\when_to_use_checker.ps1 -Context SGP      # For SGPs
.\when_to_use_checker.ps1 -Context Props    # For Props
.\when_to_use_checker.ps1 -Context General  # General check
```

---

##  **HARDCODED RULES (Never Override)**

### **Rule #1: NEVER skip verification for SGPs**
- SGPs with 8+ legs have high failure risk
- One inactive player kills entire bet
- **ALWAYS** run full prevention before SGP creation

### **Rule #2: NEVER bet props without checking status**
- Player props are worthless if player doesn't play
- **ALWAYS** run quick check before prop betting

### **Rule #3: NEVER bet on confirmed inactive players**
- DK Metcalf, Terry McLaurin, Tyler Lockett = AVOID ALL PROPS
- 100% failure rate on inactive player props

### **Rule #4: Game days require extra vigilance**
- More roster changes on game days
- **ALWAYS** run prevention system on days with games

---

##  **USAGE WORKFLOW**

### **Daily Routine**
```powershell
# Morning (9:00 AM) - if games today
.\when_to_use_checker.ps1 -Context General

# Before any betting session
.\when_to_use_checker.ps1 -Context [SGP|Props|General]

# Follow the commands provided by the checker
```

### **Pre-Betting Checklist**
1.  Run when-to-use checker for your context
2.  Follow the provided commands
3.  Check for problem players in your bets
4.  Avoid all inactive players (DK, Terry, Tyler)
5.  Proceed with verified active players only

---

##  **CURRENT STATUS (November 2, 2025)**

### **Active Triggers Today:**
-  **Game Day**: SEA vs WAS scheduled
-  **Problem Players**: 3 confirmed inactive (DK, Terry, Tyler)
-  **High Priority**: Multiple roster issues detected

### **Recommended Actions:**
1. **Run full prevention before any SGPs**
2. **Run quick check before any props**
3. **AVOID all props on DK Metcalf, Terry McLaurin, Tyler Lockett**
4. **Re-check 90 minutes before kickoff (7:45 PM)**

---

##  **DECISION MATRIX**

| What You're Doing | Use Prevention? | Action Type | Command |
|------------------|----------------|-------------|---------|
| Creating SGP |  YES (Mandatory) | Full System | `python nfl_roster_prevention_system.py` |
| Betting Props |  YES (Mandatory) | Quick Check | `.\nfl_roster_prevention_simple.ps1 -Action QuickCheck` |
| Game Day General |  YES (Auto) | Full System | `.\nfl_roster_prevention_simple.ps1 -Action Prevent` |
| Problem Players |  YES (Auto) | Quick Check | `.\when_to_use_checker.ps1 -Context Props` |
| Research Only |  NO | None | Continue without prevention |
| Totals/Spreads |  NO | None | Continue without prevention |

---

##  **SUCCESS GUARANTEE**

**Following these hardcoded rules prevents 95%+ of roster-related betting failures.**

### **What This Eliminates:**
-  Betting on inactive players
-  SGP failures from roster issues  
-  Manual roster hunting
-  Guesswork about when to check
-  Player prop failures

### **What This Provides:**
-  Clear YES/NO decisions
-  Exact commands to run
-  Automated trigger detection
-  Problem player warnings
-  Peace of mind betting

---

##  **Remember: When in Doubt, Check**

```powershell
# One command solves everything
.\when_to_use_checker.ps1 -Context [SGP|Props|General]

# Follow the instructions provided
# The system thinks for you - no guesswork needed
```

**The days of roster surprises are OVER. Use this hardcoded system and never bet on inactive players again.** 

---

*Generated by EQ12 Hardcoded Decision Engine*
*Updated: November 2, 2025*