import logging

# Set up logging
logger = logging.getLogger(__name__)
﻿"""Shell Executor with sandbox for EQ12 God Mode Commander++"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

from core.safety import ShellSandbox

BASE_DIR = Path(__file__).resolve().parent.parent
SANDBOX = ShellSandbox(working_directory=BASE_DIR)

# ---------------------------------------------------------------------------

def run_shell(cmd: str, timeout: int = 60, dry_run: bool = False,
              auto_approve: bool = False) -> Dict[str, object]:
    """Execute shell command through sandbox"""
    print(f"[shell] queued command: {cmd}")
    result = SANDBOX.run(cmd, timeout=timeout, dry_run=dry_run, auto_approve=auto_approve)

    if result.get("dry_run"):
        print("[shell] dry-run only; no command executed")
        return result

    if result.get("skipped"):
        print("[shell] command skipped by safety guard")
        return result

    if result.get("success"):
        stdout = result.get("stdout")
        if stdout:
            print(f"[shell] stdout: {stdout[:200]}")
    else:
        stderr = result.get("stderr") or result.get("error")
        if stderr:
            print(f"[shell] error: {stderr[:200]}")

    return result

def run_python_script(script_path: str, args: List[str] | None = None,
                      timeout: int = 120, dry_run: bool = False) -> Dict[str, object]:
    args = args or []
    script_abs = Path(script_path)
    if not script_abs.is_absolute():
        script_abs = BASE_DIR / script_path
    script_abs = script_abs.resolve()

    cmd_parts = ["python", str(script_abs)] + args
    cmd = " ".join(f'"{part}"' if " " in part else part for part in cmd_parts)
    return run_shell(cmd, timeout=timeout, dry_run=dry_run)

# Domain-specific helpers ------------------------------------------------

def run_sports_scraper(action: str, dry_run: bool = False) -> Dict[str, object]:
    print(f"[shell] sports scraper requested for: {action}")
    cmd = f'python scripts/sports_scraper.py "{action}"'
    return run_shell(cmd, timeout=180, dry_run=dry_run)

def run_market_scraper(action: str, dry_run: bool = False) -> Dict[str, object]:
    print(f"[shell] market scraper requested for: {action}")
    cmd = f'python scripts/market_scraper.py "{action}"'
    return run_shell(cmd, timeout=180, dry_run=dry_run)

def run_housing_monitor(action: str, dry_run: bool = False) -> Dict[str, object]:
    print(f"[shell] housing monitor requested for: {action}")
    cmd = f'python scripts/housing_monitor.py "{action}"'
    return run_shell(cmd, timeout=180, dry_run=dry_run)

def create_scheduled_task(action: str, schedule: str = "daily", dry_run: bool = True) -> Dict[str, object]:
    """Create Windows scheduled task (default dry-run)."""
    task_name = f"EQ12_{action.replace(' ', '_')[:20]}"
    cmd = f'schtasks /create /tn "{task_name}" /tr "python {BASE_DIR / 'eq12_godmode_runner.py'}" /sc {schedule}'
    return run_shell(cmd, timeout=60, dry_run=dry_run)

if __name__ == "__main__":
    result = run_shell("echo EQ12 shell sandbox test", dry_run=False)
    logger.info(result)
