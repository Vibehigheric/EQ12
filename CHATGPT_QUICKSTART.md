# 🤖 EQ12 ChatGPT Integration - Ready to Use

## 🚀 Immediate Startup (30 Seconds)

### Step 1: Load PowerShell Profile
```powershell
# Add to your PowerShell profile (permanent)
notepad $PROFILE

# Add this line:
. "C:\EQ12_BROKEN_20251122_210342\EQ12_MASTER_PROFILE_ASCII_EXPERT.ps1"

# Save and reload
. $PROFILE
```

### Step 2: Verify Installation
```powershell
# Run test suite
.\TEST_CHATGPT_INTEGRATION.ps1
```

### Step 3: Install OpenAI Package (if needed)
```powershell
pip install openai python-dotenv
```

---

## ✅ Instant Commands (Try These Now)

### AI Diagnostics
```powershell
# Diagnose VFD fault
diagnose "STO W8114"

# Analyze PLC logs
ai-analyze-plc-logs "C:\EQ12_BROKEN_20251122_210342\logs\plc_log.txt"

# Network troubleshooting
ai-network-audit
```

### Sports Betting Intelligence
```powershell
# Analyze parlay (auto-detects today's picks)
parlay-ai

# Player prop research
ai-player-prop "LeBron James" "points" "Warriors"

# Live betting advisor
ai-live-bet-advisor
```

### Code Generation
```powershell
# Generate PowerShell script
gen-script "Monitor CPU usage and send Telegram alert if >80%"

# Generate VB.NET class
ai-generate-vbnet "Create a CredentialManager class for API key storage"

# Natural language to SQL
ai-generate-sql "Show me all parlays from last week with positive ROI"
```

### Content Creation
```powershell
# Marketing copy
ai-marketing-copy "EQ12 Automation Suite" "Industrial Engineers" "professional"

# Twitter post for betting pick
ai-twitter-post "Lakers ML + Over 220.5 (+350 parlay)"
```

### Developer Tools
```powershell
# Code review
code-review "C:\EQ12_BROKEN_20251122_210342\scripts\eq12_odds_fetcher.py"

# Generate commit message
ai-commit-message

# Auto README
ai-generate-readme "EQ12 Sports Analytics" "Real-time sports betting intelligence platform"
```

### Master Command (Ask Anything)
```powershell
# General-purpose AI query
ai "How do I optimize my parlay strategy for NBA games?"
ai "Explain Kelly Criterion for bankroll management"
ai "Write a PowerShell function to backup my EQ12 database"
```

---

## 🎯 Batch Operations

### Morning Routine
```powershell
ai-daily-diagnostics
```
Runs:
- System log summary
- Parlay analysis
- Revenue report
- Market efficiency scan

### Content Generation
```powershell
ai-content-batch
```
Generates:
- 5 Twitter posts for today's picks
- Marketing copy variants
- Social media content

---

## 📊 All 20+ Integration Points

### Category 1: AI Diagnostics (ASC II Expert)
| Command | Purpose | Example |
|---------|---------|---------|
| `ai-diagnose-vfd` | VFD fault diagnosis | `diagnose "Network Timeout"` |
| `ai-analyze-plc-logs` | PLC log analysis | `ai-analyze-plc-logs plc.log` |
| `ai-network-audit` | Network troubleshooting | `ai-network-audit` |

### Category 2: Sports Betting Intelligence
| Command | Purpose | Example |
|---------|---------|---------|
| `ai-analyze-parlay` | Parlay EV analysis | `parlay-ai` |
| `ai-player-prop` | Player prop research | `ai-player-prop "Curry" "3PT" "Lakers"` |
| `ai-live-bet-advisor` | Live betting decisions | `ai-live-bet-advisor` |

### Category 3: Code Generation
| Command | Purpose | Example |
|---------|---------|---------|
| `ai-generate-powershell` | Generate PS script | `gen-script "Parse JSON logs"` |
| `ai-generate-vbnet` | Generate VB.NET class | `ai-generate-vbnet "AlertManager"` |
| `ai-generate-sql` | Natural language → SQL | `ai-generate-sql "Top 10 profitable bets"` |

### Category 4: Business Intelligence
| Command | Purpose | Example |
|---------|---------|---------|
| `ai-revenue-report` | Revenue analytics | `ai-revenue-report` |
| `ai-market-efficiency` | Arbitrage detection | `ai-market-efficiency` |

### Category 5: Content Creation
| Command | Purpose | Example |
|---------|---------|---------|
| `ai-marketing-copy` | Marketing content | `ai-marketing-copy "EQ12" "Engineers"` |
| `ai-twitter-post` | Twitter posts | `ai-twitter-post "Lakers ML"` |

### Category 6: System Monitoring
| Command | Purpose | Example |
|---------|---------|---------|
| `ai-summarize-logs` | Log summarization | `ai-summarize-logs` |
| `ai-detect-anomalies` | Anomaly detection | `ai-detect-anomalies metrics.csv` |

### Category 7: Developer Tools
| Command | Purpose | Example |
|---------|---------|---------|
| `ai-code-review` | Code review | `code-review script.py` |
| `ai-commit-message` | Commit messages | `ai-commit-message` |
| `ai-generate-readme` | Auto README | `ai-generate-readme "MyProject" "desc"` |

---

## 🔥 Power User Tips

### 1. Chain Commands
```powershell
# Generate, review, and commit code
gen-script "Backup database" | Out-File backup.ps1
code-review backup.ps1
git add backup.ps1
ai-commit-message
```

### 2. Custom Workflows
```powershell
# Create custom function
function my-betting-workflow {
    ai-analyze-parlay
    ai-market-efficiency
    ai-revenue-report
}
```

### 3. Use Aliases
```powershell
ai "question"              # instead of ai-ask
diagnose "fault"           # instead of ai-diagnose-vfd
parlay-ai                  # instead of ai-analyze-parlay
code-review file.py        # instead of ai-code-review
gen-script "task"          # instead of ai-generate-powershell
```

### 4. Batch Processing
```powershell
# Review all Python files
Get-ChildItem *.py | ForEach-Object { code-review $_.FullName }

# Generate docs for all modules
Get-ChildItem vbnet_projects\*.vb | ForEach-Object {
    ai "Generate XML documentation for: $($_.Name)"
}
```

---

## 🛠️ Troubleshooting

### "Command not found"
```powershell
# Reload profile
. $PROFILE

# Or manually load ChatGPT commands
. "C:\EQ12_BROKEN_20251122_210342\EQ12_CHATGPT_COMMANDS.ps1"
```

### "OpenAI API Error"
```powershell
# Verify API key in .env
Get-Content C:\EQ12_BROKEN_20251122_210342\.env | Select-String "OPENAI_API_KEY"

# Test API connection
ai "test"
```

### "Python module not found"
```powershell
pip install openai python-dotenv requests
```

### "Rate limit exceeded"
```powershell
# Wait 60 seconds or upgrade OpenAI tier
Start-Sleep -Seconds 60
```

---

## 📈 Cost Optimization

### Model Selection Strategy
- **gpt-4**: Complex reasoning (VFD diagnosis, parlay analysis, code review)
- **gpt-4-turbo**: Faster, cheaper for similar tasks
- **gpt-3.5-turbo**: Simple tasks (commit messages, Twitter posts, SQL)

### Estimated Costs
| Task | Model | Cost/Call |
|------|-------|-----------|
| VFD Diagnosis | gpt-4 | $0.03-0.06 |
| Parlay Analysis | gpt-4-turbo | $0.01-0.03 |
| Code Generation | gpt-4 | $0.02-0.05 |
| Commit Message | gpt-3.5-turbo | $0.001-0.002 |
| Twitter Post | gpt-3.5-turbo | $0.001-0.002 |

### Budget-Friendly Settings
Edit `eq12_openai_client.py`:
```python
# Use cheaper model by default
model = "gpt-4-turbo"  # instead of "gpt-4"

# Reduce max_tokens for simple tasks
max_tokens = 500  # instead of 1000
```

---

## 🔐 Security Best Practices

### API Key Protection
```powershell
# Never commit .env
git update-index --assume-unchanged .env

# Rotate keys monthly
ai "Generate a Python script to rotate my OpenAI API key"
```

### Sensitive Data
```powershell
# Never send sensitive data to ChatGPT
# Bad: diagnose "Customer X VFD fault at Site Y"
# Good: diagnose "VFD Network Timeout"
```

---

## 📚 Documentation Links

- **Complete Catalog**: `C:\EQ12_BROKEN_20251122_210342\docs\EQ12_CHATGPT_INTEGRATION_CATALOG.md`
- **OpenAI Client**: `C:\EQ12_BROKEN_20251122_210342\eq12_openai_client.py`
- **Command Reference**: `C:\EQ12_BROKEN_20251122_210342\EQ12_CHATGPT_COMMANDS.ps1`

---

## 🎉 Success Checklist

- [ ] PowerShell profile loaded (`eq12-help` works)
- [ ] Test suite passed (`.\TEST_CHATGPT_INTEGRATION.ps1`)
- [ ] OpenAI package installed (`pip show openai`)
- [ ] API key configured (`.env` contains `OPENAI_API_KEY`)
- [ ] Tried first command (`ai "Hello from EQ12!"`)

---

**You're ready!** Start with: `ai "What can you help me with?"`
