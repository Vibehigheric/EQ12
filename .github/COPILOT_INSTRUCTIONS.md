# EQ12 Copilot Instructions

## Project Context
EQ12 is a lightweight automation and scraping/dashboard stack focused on getting timely data into a small dashboard. This includes:
- Scrapers and utilities (Python) under `scripts/` and `scraper_starter/`
- PowerShell utilities and wrappers under `scripts/` for Windows automation
- Tests in `tests/` (`pytest`) and `tests/pester/` (Pester)
- CI workflows under `.github/workflows/` and devcontainer config under `.devcontainer/`

## Coding Standards (STRICT)

### Python Rules
- Always use timezone-aware datetimes (UTC). Never compare naive vs aware.
- Use argparse + logging for CLIs. Use type hints where practical.
- Prefer f-strings. Follow PEP8 (4-space indentation).
- Follow Ruff + pyproject.toml. Don't add legacy ruff-lsp settings.

### PowerShell Rules
- Always use `CmdletBinding()` for advanced functions
- Prefer explicit parameter types and `Write-Error`/`Write-Verbose`

### Secrets & Security
- Never hardcode secrets. Read from env variables: `ODDS_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `OPENAI_API_KEY`, `CODEX_API_KEY`
- Always write JSON snapshots to `C:\EQ12\logs` (Windows) or `/workspaces/EQ12/logs` (Codespaces)
- Use UTC timestamps in all logs

### Betting Domain Rules
- Never combine correlated legs illegally
- Deduplicate moneyline legs across books in the same parlay
- Prefer hooks (±0.5) for spreads to avoid pushes

### Cost & API Guards
- Any new OpenAI usage must pass `eq12_cost_guards` checks
- Check `is_free_mode()` before making any API calls

### I/O & File Handling
- Read/write under `logs/`, `data/`, `configs/` only. No secrets in code.
- Logging: utf-8 safe, no emoji in Windows console paths that can crash encoders
- If touching timestamps in parlay JSON, convert ISO8601 Z → aware UTC via `datetime.fromisoformat(...).astimezone(timezone.utc)` or `dateutil`

### Testing & Quality
- Every new feature or bugfix must include pytest and Pester tests where relevant
- Commits require signed commits (`git commit -S`). CI should verify signatures

## File Organization
- `scripts/` — main runnable scripts (both .py and .ps1 wrappers)
- `tests/` — pytest files (unit/integration)
- `tests/pester/` — Pester tests for PowerShell
- `logs/` or `C:\EQ12\logs` — runtime snapshots and artifacts
- `.github/workflows/` — CI jobs
- `configs/` — configuration files, API keys, settings

## Common Patterns

### Datetime Handling
```python
from datetime import datetime, timezone
# Always use timezone-aware UTC
now = datetime.now(timezone.utc)
# When parsing ISO strings
parsed = datetime.fromisoformat(iso_string.replace('Z', '+00:00')).astimezone(timezone.utc)
```

### Logging Setup
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

### Cost Guard Pattern
```python
from eq12_free_guard import is_free_mode, get_cost_guards
if not is_free_mode():
    guards = get_cost_guards()
    allowed, reason = guards.check_request_allowed('openai', estimated_cost)
    if not allowed:
        raise RuntimeError(f"Cost guard block: {reason}")
```

## What NOT to do
- Don't use `datetime.utcnow()` (deprecated) - use `datetime.now(timezone.utc)`
- Don't put secrets in code or logs
- Don't create correlating parlay legs (same game, related outcomes)
- Don't bypass cost guards for API calls
- Don't use emoji in log paths that go to Windows console
- Don't ignore the parlay sanitizer helpers in `eq12_parlay_sanitizer.py`

## When Unsure
- Ask for sanitizer helpers in `eq12_parlay_sanitizer.py` for sportsbook constraints
- Use the doctor script (`eq12_doctor.py`) to validate system state
- Check the free mode status before implementing paid features
- Reference existing patterns in `scripts/` for similar functionality
