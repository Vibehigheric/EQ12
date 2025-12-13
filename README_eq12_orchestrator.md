EQ12 Orchestrator

Overview
--------
This orchestrator ties together stocks, crypto, and odds fetchers, summarizes them with OpenAI, logs results, and optionally sends a Telegram notification.

Quick start
-----------
1. Ensure your keys are stored in `C:\EQ12\keys`:
   - `openai.txt`
   - `telegram.txt` (optional)
   - `telegram_id.txt` (optional)
   - `odds.txt` (optional)

2. Install Python dependencies in your EQ12 venv (if present):

```powershell
if (Test-Path 'C:\EQ12\.venv\Scripts\python.exe') { & 'C:\EQ12\.venv\Scripts\python.exe' -m pip install -r C:\EQ12\requirements-orchestrator.txt } else { python -m pip install -r C:\EQ12\requirements-orchestrator.txt }
```

3. Dry-run (no external calls):

```powershell
& 'C:\EQ12\scripts\eq12-orchestrator.ps1' -Dry
```

4. Normal run:

```powershell
& 'C:\EQ12\scripts\eq12-orchestrator.ps1'
```

Scheduling
----------
Use Task Scheduler or `setup_rotation_reminder.ps1` pattern to schedule daily runs.

Notes
-----
- The orchestrator is intentionally minimal and pluggable. Replace placeholder fetchers with your real modules.
- Protect keys and rotate regularly.
