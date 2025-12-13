#!/usr/bin/env python3
"""
EQ12 CheckLog Viewer - Professional Log Monitoring Tool
======================================================
Real-time log monitoring with color-coded severity levels.
ASCII-safe, UTF-8 corruption-proof terminal viewer.

Author: EQ12 AI Development Team
Version: 1.0.0 - ASCII-SAFE VIEWER
Date: November 16, 2025
Buffalo NY 14215 - Content Empire Command Center
"""

import re
import sys
import time
from pathlib import Path

# ASCII-only color codes
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
CYAN = "\033[36m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RESET = "\033[0m"
BOLD = "\033[1m"


def clean_ascii(line):
    """Convert line to ASCII-safe version"""
    if isinstance(line, bytes):
        line = line.decode("utf-8", errors="replace")
    return "".join([ch if ord(ch) < 128 else "?" for ch in str(line)])


def colorize_line(line):
    """Apply color coding based on content"""
    line = clean_ascii(line)

    # Timestamp highlighting (YYYY-MM-DD HH:MM:SS or similar patterns)
    line = re.sub(
        r"(\d{4}-\d{2}-\d{2}.*?\d{2}:\d{2}:\d{2})", CYAN + r"\1" + RESET, line
    )
    line = re.sub(r"(\[\d{2}:\d{2}:\d{2}\])", CYAN + r"\1" + RESET, line)

    # Error patterns
    error_patterns = [
        r"\[ERROR\]",
        r"ERROR:",
        r"error",
        r"failed",
        r"failure",
        r"exception",
        r"critical",
        r"fatal",
    ]

    for pattern in error_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return RED + BOLD + line + RESET

    # Warning patterns
    warning_patterns = [
        r"\[WARNING\]",
        r"\[WARN\]",
        r"WARNING:",
        r"warn",
        r"caution",
        r"deprecated",
    ]

    for pattern in warning_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return YELLOW + line + RESET

    # Success/Info patterns
    success_patterns = [
        r"\[INFO\]",
        r"\[SUCCESS\]",
        r"INFO:",
        r"success",
        r"complete",
        r"ok",
        r"ready",
    ]

    for pattern in success_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return GREEN + line + RESET

    # PowerShell specific error patterns
    ps_error_patterns = [
        r"Missing closing",
        r"Unexpected token",
        r"string is missing the terminator",
        r"The term .* is not recognized",
        r"cannot be loaded",
    ]

    for pattern in ps_error_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return RED + "[POWERSHELL_ERROR] " + line + RESET

    # JSON/Parse error patterns
    if re.search(r"Could not parse|parse error|json.*error", line, re.IGNORECASE):
        return YELLOW + "[PARSE_ERROR] " + line + RESET

    # EQ12 specific patterns
    if re.search(r"EQ12|Content Empire|Buffalo NY", line, re.IGNORECASE):
        return BLUE + line + RESET

    # Default: return line as-is
    return line


def tail_log_file(file_path, follow=True, lines_to_show=50):
    """Tail a log file with real-time updates"""
    path = Path(file_path)

    if not path.exists():
        print(RED + f"ERROR: Log file not found: {file_path}" + RESET)
        return False

    # Display header
    print(CYAN + BOLD + "=" * 80 + RESET)
    print(CYAN + f"EQ12 CHECKLOG VIEWER - {path.name}" + RESET)
    print(CYAN + f"File: {file_path}" + RESET)
    print(CYAN + f"Size: {path.stat().st_size:,} bytes" + RESET)
    if follow:
        print(CYAN + "Mode: LIVE MONITORING (Press CTRL+C to exit)" + RESET)
    else:
        print(CYAN + f"Mode: STATIC VIEW (Last {lines_to_show} lines)" + RESET)
    print(CYAN + BOLD + "=" * 80 + RESET)
    print()

    try:
        with open(path, encoding="utf-8", errors="replace") as file:
            if not follow:
                # Static mode - show last N lines
                lines = file.readlines()
                start_index = max(0, len(lines) - lines_to_show)
                for line in lines[start_index:]:
                    print(colorize_line(line.rstrip()))
                return True

            # Live mode - seek to end and follow new lines
            file.seek(0, 2)  # Jump to end of file

            while True:
                line = file.readline()
                if not line:
                    time.sleep(0.1)
                    continue

                print(colorize_line(line.rstrip()))

    except KeyboardInterrupt:
        print(f"\n{CYAN}Log monitoring stopped by user{RESET}")
        return True
    except Exception as e:
        print(f"{RED}Error reading file: {clean_ascii(str(e))}{RESET}")
        return False


def find_recent_logs(log_dir="C:/EQ12/logs", max_files=10):
    """Find most recent log files"""
    log_path = Path(log_dir)

    if not log_path.exists():
        return []

    # Find all log files
    log_files = []
    for pattern in ["*.log", "*.json", "*.txt"]:
        log_files.extend(log_path.glob(pattern))

    # Sort by modification time (newest first)
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    return log_files[:max_files]


def show_usage():
    """Display usage information"""
    print(f"{CYAN}EQ12 CheckLog Viewer - Usage{RESET}")
    print()
    print(f"{GREEN}Usage:{RESET}")
    print("  python eq12_checklog_viewer.py <log_file_path>")
    print("  python eq12_checklog_viewer.py --recent")
    print("  python eq12_checklog_viewer.py --static <log_file_path>")
    print()
    print(f"{GREEN}Examples:{RESET}")
    print("  python eq12_checklog_viewer.py C:/EQ12/logs/system_integrity_report.json")
    print("  python eq12_checklog_viewer.py --recent")
    print("  python eq12_checklog_viewer.py --static C:/EQ12/logs/emergency_repair.log")
    print()
    print(f"{GREEN}Options:{RESET}")
    print("  --recent     Show menu of recent log files")
    print("  --static     View file content without live monitoring")
    print("  --help       Show this help message")


def main():
    """Main entry point"""
    if len(sys.argv) < 2 or "--help" in sys.argv:
        show_usage()
        return 0

    if "--recent" in sys.argv:
        # Show recent log files
        recent_logs = find_recent_logs()
        if not recent_logs:
            print(f"{RED}No log files found in C:/EQ12/logs{RESET}")
            return 1

        print(f"{CYAN}Recent EQ12 Log Files:{RESET}")
        print()
        for i, log_file in enumerate(recent_logs, 1):
            mtime = log_file.stat().st_mtime
            size = log_file.stat().st_size
            print(f"{GREEN}{i:2}.{RESET} {log_file.name}")
            print(f"     Path: {log_file}")
            print(f"     Size: {size:,} bytes")
            print(f"     Modified: {time.ctime(mtime)}")
            print()

        try:
            choice = input(
                f"{CYAN}Select file number (1-{len(recent_logs)}) or press Enter to exit: {RESET}"
            )
            if choice.strip():
                file_index = int(choice.strip()) - 1
                if 0 <= file_index < len(recent_logs):
                    selected_file = recent_logs[file_index]
                    print(f"\n{GREEN}Opening: {selected_file.name}{RESET}\n")
                    return tail_log_file(str(selected_file))
        except (ValueError, KeyboardInterrupt):
            pass

        return 0

    # Determine mode
    follow_mode = "--static" not in sys.argv

    # Get file path
    file_path = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            file_path = arg
            break

    if not file_path:
        print(f"{RED}Error: No log file specified{RESET}")
        show_usage()
        return 1

    # Monitor the file
    success = tail_log_file(file_path, follow=follow_mode)
    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{CYAN}Viewer terminated by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{RED}Unexpected error: {clean_ascii(str(e))}{RESET}")
        sys.exit(1)
