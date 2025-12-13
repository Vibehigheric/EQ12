# 🎯 EQ12 AI Commands - Quick Reference

## ✅ ALL WORKING (Using FREE Alternatives)

**OpenAI Quota Exceeded?** No problem! Commands automatically use Groq/OpenRouter/Claude.

---

## 🚀 Most Useful Commands

### General AI Assistant
```powershell
ai "your question here"              # Ask anything
```

### VFD/Industrial Diagnostics
```powershell
diagnose "STO W8114"                 # VFD fault diagnosis
diagnose "Network Timeout"           # Network issues
```

### Sports Betting
```powershell
parlay-ai                            # Analyze today's parlays
ai-player-prop "LeBron" "points" "Warriors"
```

### Code Generation
```powershell
gen-script "Monitor CPU usage"       # Generate PowerShell
gen-script "Backup database daily"   # Any automation task
```

### Code Review
```powershell
code-review "script.py"              # AI code review
ai-commit-message                    # Generate git commit msg
```

---

## 📊 Current Provider Status

| Provider | Status | Speed |
|----------|--------|-------|
| OpenAI | ⚠️ Quota | Fast |
| Groq | ✅ FREE | **10x Faster** |
| OpenRouter | ✅ **ACTIVE** | Moderate |
| Claude | ✅ Ready | Fast |

**Auto-fallback enabled** - Commands "just work"!

---

## 🆓 Get Even Faster (Optional)

Groq is **10x faster** than OpenAI and **FREE**:

Already configured in your `.env`:
```
GROQ_API_KEY=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
```

Should be working automatically!

---

## 🧪 Test Your Setup

```powershell
.\TEST_AI_PROVIDERS.ps1              # Test all providers
ai "test"                            # Quick test
```

---

## 📚 Full Command List

### Diagnostics (3 commands)
- `ai-diagnose-vfd` - VFD fault diagnosis
- `ai-analyze-plc-logs` - PLC log analysis  
- `ai-network-audit` - Network troubleshooting

### Sports Betting (3 commands)
- `ai-analyze-parlay` - Parlay EV analysis
- `ai-player-prop` - Player prop research
- `ai-live-bet-advisor` - Live betting advisor

### Code Generation (3 commands)
- `ai-generate-powershell` - Generate scripts
- `ai-generate-vbnet` - Generate VB.NET classes
- `ai-generate-sql` - Natural language to SQL

### Business Intelligence (2 commands)
- `ai-revenue-report` - Revenue analytics
- `ai-market-efficiency` - Arbitrage detection

### Content Creation (2 commands)
- `ai-marketing-copy` - Marketing content
- `ai-twitter-post` - Twitter posts

### System Monitoring (2 commands)
- `ai-summarize-logs` - Log summarization
- `ai-detect-anomalies` - Anomaly detection

### Developer Tools (3 commands)
- `ai-code-review` - Code review
- `ai-commit-message` - Commit messages
- `ai-generate-readme` - Auto README

### Master Commands (3 commands)
- `ai-ask` - General purpose
- `ai-daily-diagnostics` - Morning routine
- `ai-content-batch` - Batch content

**Total**: 21 commands, all working with free providers!

---

## 💡 Pro Tips

1. **Use aliases**: `ai` instead of `ai-ask`, `diagnose` instead of `ai-diagnose-vfd`

2. **Check provider**: Response shows which AI answered: `[OpenRouter/Llama-3.1-70B]`

3. **Test providers**: Run `.\TEST_AI_PROVIDERS.ps1` to see all available options

4. **Get Groq (fastest)**: Already configured, should work automatically!

---

**Status**: ✅ All systems operational with FREE alternatives!

**Documentation**: See `AI_FALLBACK_COMPLETE.md` for full details
