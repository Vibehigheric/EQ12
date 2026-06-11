#!/usr/bin/env python3
"""Repo-safe nightly evaluation wrapper for GitHub Actions.

This runner only executes scripts that exist locally and treats missing
experimental evaluators as warnings instead of hard failures. It writes a
machine-readable JSON summary and a short markdown summary to the repo logs
directory so workflows can always publish artifacts and step summaries.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = Path(os.environ.get("EQ12_LOGS_DIR", REPO_ROOT / "logs"))


@dataclass
class TaskResult:
    name: str
    script: str
    status: str
    returncode: int | None
    stdout_log: str | None
    stderr_log: str | None
    reason: str


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_logs_dir() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def available_tasks(mode: str) -> list[tuple[str, Path]]:
    tasks = [
        ("performance-monitor", REPO_ROOT / "scripts" / "eq12_performance_monitor.py"),
    ]
    if mode == "weekly":
        tasks.append(
            ("performance-monitor-weekly", REPO_ROOT / "scripts" / "eq12_performance_monitor.py")
        )
    return tasks


def run_script(name: str, script_path: Path, suffix: str) -> TaskResult:
    stdout_log = LOGS_DIR / f"{name}_{suffix}.stdout.log"
    stderr_log = LOGS_DIR / f"{name}_{suffix}.stderr.log"

    if not script_path.exists():
        return TaskResult(
            name=name,
            script=str(script_path.relative_to(REPO_ROOT)),
            status="warning",
            returncode=None,
            stdout_log=None,
            stderr_log=None,
            reason="script_missing",
        )

    with stdout_log.open("w", encoding="utf-8") as stdout_handle, stderr_log.open(
        "w", encoding="utf-8"
    ) as stderr_handle:
        process = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=REPO_ROOT,
            stdout=stdout_handle,
            stderr=stderr_handle,
            text=True,
            check=False,
            env={**os.environ, "EQ12_LOGS_DIR": str(LOGS_DIR)},
        )

    status = "success" if process.returncode == 0 else "warning"
    reason = "completed" if process.returncode == 0 else f"script_exit_{process.returncode}"
    return TaskResult(
        name=name,
        script=str(script_path.relative_to(REPO_ROOT)),
        status=status,
        returncode=process.returncode,
        stdout_log=str(stdout_log.relative_to(REPO_ROOT)),
        stderr_log=str(stderr_log.relative_to(REPO_ROOT)),
        reason=reason,
    )


def write_outputs(mode: str, results: list[TaskResult], suffix: str) -> tuple[Path, Path]:
    success_count = sum(1 for result in results if result.status == "success")
    warning_count = sum(1 for result in results if result.status == "warning")

    summary = {
        "generated_at": iso_now(),
        "mode": mode,
        "system_status": "OK" if success_count else "WARN",
        "job_status": "success" if success_count else "warning",
        "results": [asdict(result) for result in results],
        "success_count": success_count,
        "warning_count": warning_count,
        "output_files": [
            entry
            for result in results
            for entry in (result.stdout_log, result.stderr_log)
            if entry
        ],
    }

    json_path = LOGS_DIR / f"nightly_evaluation_summary_{suffix}.json"
    md_path = LOGS_DIR / f"nightly_evaluation_summary_{suffix}.md"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        f"- Generated at: {summary['generated_at']}",
        f"- Mode: {mode}",
        f"- Job status: {summary['job_status']}",
        f"- Successful tasks: {success_count}",
        f"- Warnings: {warning_count}",
        "- Output files:",
    ]
    if summary["output_files"]:
        lines.extend([f"  - {path}" for path in summary["output_files"]])
    else:
        lines.append("  - none")

    if warning_count:
        lines.append("- Warning reasons:")
        for result in results:
            if result.status == "warning":
                lines.append(f"  - {result.name}: {result.reason}")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["daily", "weekly"], default="daily")
    args = parser.parse_args()

    ensure_logs_dir()
    suffix = utc_stamp()

    results = [
        run_script(name, script_path, suffix)
        for name, script_path in available_tasks(args.mode)
    ]
    json_path, md_path = write_outputs(args.mode, results, suffix)

    runner_log = LOGS_DIR / f"nightly_evaluation_runner_{suffix}.log"
    runner_log.write_text(
        "\n".join(
            [
                f"generated_at={iso_now()}",
                f"mode={args.mode}",
                f"summary_json={json_path}",
                f"summary_markdown={md_path}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"summary_json": str(json_path), "summary_markdown": str(md_path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
