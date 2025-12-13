# 🤖 EQ12 GODSTACK Custom Copilot Prompts

Use these in Copilot Chat for common tasks in this repo.

---

## 🔍 Code Analysis
- "Explain what `enrichment.py` does in plain English."
- "Check `badge_check.py` for missing error handling."
- "Review `compliance_audit.py` for potential false positives."

---

## 🧪 Testing
- "Write pytest unit tests for `db.py` helpers."
- "Add coverage tests for `trending_monitor.py`."
- "Generate integration tests for `dashboard.py` FastAPI endpoints."

---

## 🔒 Security & Compliance
- "Scan this file for hardcoded secrets."
- "Suggest improvements to comply with CODEOWNERS and sensitive_module rules."
- "Check this PR against governance gates (Secrets, Security, CI, Compliance)."

---

## 🖥️ Scraping & Automation
- "Harden this Playwright selector for Swagbucks scraping."
- "Refactor scraper to fallback on DevTools MCP if selector fails."
- "Optimize `autosuggest_merge.py` for faster query deduplication."

---

## 📊 Governance & Reporting
- "Summarize the current badge statuses and suggest fixes."
- "Generate a quarterly compliance report from codebase checks."
- "Create a PR description using sensitive_module.md template."

---

## ⚡ Stack-Specific Prompts

### Betting Stack
- "Add an OddsAPI integration to fetch MLB odds and store in SQLite."
- "Generate responsible gaming compliance checks for betting features."
- "Create DraftKings/FanDuel API wrapper with rate limiting."

### Travel Stack
- "Generate scraper for flight deals BUF → LAX and push to Telegram."
- "Add booking confirmation monitoring with price change alerts."
- "Create Expedia/Kayak API integration for travel monitoring."

### Cannabis Stack
- "Add Bing News + Google RSS search for Buffalo dispensary updates."
- "Generate METRC compliance tracking for cannabis operations."
- "Create state regulation compliance checker for multi-state operations."

### Fleet Stack
- "Pull NHTSA recall data and send alert if VIN matches fleet list."
- "Add telematics integration for real-time vehicle monitoring."
- "Generate maintenance scheduling with automated alerts."

### Credit Stack
- "Check mortgage affordability scrapers for compliance."
- "Add credit monitoring with Experian/Equifax/TransUnion APIs."
- "Generate PCI compliance validation for financial data handling."

### AliDropship Stack
- "Write SEO-friendly product title rewriter using GPT."
- "Add AliExpress product monitoring with price change alerts."
- "Generate automated inventory sync between suppliers and stores."

---

# ✅ Tips
- Use `// Copilot:` comments inside code to guide completions.
- Pair Copilot with your PR templates for best compliance.