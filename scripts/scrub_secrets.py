#!/usr/bin/env python3
"""
Non-destructive secret scanner: searches for likely secret patterns and writes a JSON report.
Does NOT modify files. Intended to be safe to run unattended.
"""
import re
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "logs"
REPORTS.mkdir(exist_ok=True)

# Patterns to search for (simple heuristics)
PATTERNS = {
    "openai": re.compile(r"sk-(live|proj|test)[A-Za-z0-9_-]{16,}", re.IGNORECASE),
    "grok_groq": re.compile(r"gsk_[A-Za-z0-9_-]{16,}", re.IGNORECASE),
    "api_key_simple": re.compile(r"(API_KEY|OPENAI_API_KEY|GROQ_API_KEY|ODDS_API_KEY|OPENWEATHER_API_KEY|GITHUB_TOKEN|TELEGRAM_BOT_TOKEN)\s*[=:]\s*\"?([A-Za-z0-9_\-:\.@/]+)\"?", re.IGNORECASE),
    "google": re.compile(r"AIza[0-9A-Za-z\-_]{35}", re.IGNORECASE),
    "anthropic": re.compile(r"sk-ant-[A-Za-z0-9_-]{16,}", re.IGNORECASE),
}

IGNORE_DIRS = {".git", "node_modules", "venv", ".venv", "dist", "build"}

results = []

for path in ROOT.rglob("*"):
    try:
        if path.is_dir():
            if path.name in IGNORE_DIRS:
                continue
        else:
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bin", ".exe", ".dll"}:
                continue
            text = path.read_text(errors="replace")
            matches = []
            for name, pat in PATTERNS.items():
                for m in pat.finditer(text):
                    snippet = text[max(0, m.start()-40):m.end()+40].replace("\n", " ")
                    matches.append({"pattern": name, "match": m.group(0), "snippet": snippet})
            if matches:
                results.append({"path": str(path), "matches": matches})
    except Exception:
        # skip unreadable files
        continue

report = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "root": str(ROOT),
    "findings_count": len(results),
    "findings": results,
}

outfile = REPORTS / f"scrub_secrets_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(f"Secret scan complete. Report: {outfile}")
