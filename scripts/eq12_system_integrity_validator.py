#!/usr/bin/env python3
"""
EQ12 System Integrity Validator - Python 3.12 Compatible
========================================================
Professional-grade system integrity checker and repairer.
Scans all EQ12 files for corruption and creates clean repair outputs.

Author: EQ12 AI Development Team
Version: 1.0.0 - ASCII-SAFE INTEGRITY MODE
Date: November 16, 2025
Buffalo NY 14215 - Content Empire Command Center
"""

import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# ASCII-safe configuration
ROOT = Path("C:/EQ12")
CHECK_EXT = [".py", ".ps1", ".json", ".env", ".txt", ".md"]
REPORT = ROOT / "logs/system_integrity_report.json"
FIX_DIR = ROOT / "repairs"


def ascii_clean(text):
    """Convert text to ASCII-safe version, replacing non-ASCII with ?"""
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    return "".join([c if ord(c) < 128 else "?" for c in str(text)])


def safe_print(text, prefix="INFO"):
    """Print ASCII-safe text with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    clean_text = ascii_clean(text)
    print(f"[{timestamp}] [{prefix}] {clean_text}")


def check_file(path):
    """Check a single file for issues and return problems + clean version"""
    try:
        p = Path(path)
        if not p.exists():
            return ["file_not_found"], ""

        # Read with error handling
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return [f"read_error: {e!s}"], ""

        clean = ascii_clean(text)
        issues = []

        # PowerShell specific checks
        if p.suffix == ".ps1":
            # Check for common PowerShell syntax errors
            if "Missing closing" in text:
                issues.append("powershell_missing_brace_error")
            if "Unexpected token" in text:
                issues.append("powershell_unexpected_token_error")
            if "string is missing the terminator" in text:
                issues.append("powershell_string_terminator_error")

            # Structural integrity check
            open_braces = text.count("{")
            close_braces = text.count("}")
            if open_braces != close_braces:
                issues.append(f"brace_mismatch_open_{open_braces}_close_{close_braces}")

            # Check for param block issues
            if "param(" in text and not re.search(
                r"param\s*\([^)]*\)\s*(\r?\n|\s)", text
            ):
                issues.append("param_block_malformed")

        # JSON validity check
        elif p.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as e:
                issues.append(f"json_invalid: {e!s}")

        # Python syntax check
        elif p.suffix == ".py":
            try:
                compile(text, str(p), "exec")
            except SyntaxError as e:
                issues.append(f"python_syntax_error: {e!s}")

        # Unicode/emoji corruption check
        if text != clean:
            non_ascii_count = len(text) - len(clean.replace("?", ""))
            issues.append(f"unicode_corruption_{non_ascii_count}_chars")

        # Check for BOM
        if text.startswith("\ufeff"):
            issues.append("bom_detected")

        return issues, clean

    except Exception as e:
        return [f"check_error: {e!s}"], ""


def repair_file(original_path, clean_text, issues):
    """Create repaired version of file in repairs directory"""
    try:
        # Ensure repair directory exists
        FIX_DIR.mkdir(exist_ok=True)

        # Create safe filename for repairs
        safe_name = (
            str(original_path).replace(":", "").replace("\\", "_").replace("/", "_")
        )
        repaired_path = FIX_DIR / safe_name

        # Apply additional fixes based on file type and issues
        fixed_text = clean_text

        # Fix PowerShell brace issues
        if "brace_mismatch" in str(issues):
            open_count = fixed_text.count("{")
            close_count = fixed_text.count("}")
            if open_count > close_count:
                fixed_text += "\n" + "}" * (open_count - close_count)
            elif close_count > open_count:
                # Remove excess closing braces carefully
                lines = fixed_text.split("\n")
                removed = 0
                needed = close_count - open_count
                for i, line in enumerate(lines):
                    if line.strip() == "}" and removed < needed:
                        lines[i] = ""
                        removed += 1
                fixed_text = "\n".join(lines)

        # Remove BOM
        if fixed_text.startswith("\ufeff"):
            fixed_text = fixed_text[1:]

        # Write repaired file
        repaired_path.write_text(fixed_text, encoding="utf-8")
        return str(repaired_path)

    except Exception as e:
        safe_print(f"Failed to create repair for {original_path}: {e}", "ERROR")
        return None


def scan_all_files():
    """Scan all files in EQ12 directory for issues"""
    safe_print("Starting comprehensive file scan...")
    results = {}
    total_files = 0
    files_with_issues = 0

    for ext in CHECK_EXT:
        pattern = f"*{ext}"
        for path in ROOT.rglob(pattern):
            # Skip certain directories
            if any(
                skip in str(path)
                for skip in [".git", "__pycache__", ".venv", "node_modules"]
            ):
                continue

            total_files += 1
            issues, clean_text = check_file(path)

            if issues:
                files_with_issues += 1
                repaired_path = repair_file(str(path), clean_text, issues)

                results[str(path)] = {
                    "issues": issues,
                    "repaired_output": repaired_path,
                    "file_size": path.stat().st_size if path.exists() else 0,
                    "last_modified": path.stat().st_mtime if path.exists() else 0,
                }

                safe_print(
                    f"Issues found in {path.name}: {len(issues)} problems", "WARNING"
                )

            # Progress indicator
            if total_files % 50 == 0:
                safe_print(f"Scanned {total_files} files...")

    safe_print(
        f"Scan complete: {total_files} files scanned, {files_with_issues} have issues"
    )
    return results, total_files, files_with_issues


def check_pi_cluster():
    """Test Raspberry Pi cluster connectivity"""
    safe_print("Testing Raspberry Pi cluster connectivity...")

    pi_hosts = ["192.168.1.80", "192.168.1.81", "192.168.1.82"]

    connectivity_results = {}

    for host in pi_hosts:
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "3000", host],
                capture_output=True,
                text=True,
                timeout=5,
            )
            connectivity_results[host] = result.returncode == 0

        except Exception as e:
            connectivity_results[host] = False
            safe_print(f"Failed to ping {host}: {e}", "WARNING")

    return connectivity_results


def check_critical_modules():
    """Check for critical EQ12 Python modules"""
    critical_modules = [
        "eq12_business_intelligence_tracker.py",
        "eq12_quantum_revenue_deployment_engine.py",
        "eq12_master_revenue_orchestrator.py",
        "eq12_advanced_revenue_reporter_claude.py",
        "eq12_total_system_launcher.py",
        "eq12_enhanced_command_launcher_v6.py",
    ]

    module_status = {}
    for module in critical_modules:
        module_path = ROOT / "scripts" / module
        if not module_path.exists():
            module_path = ROOT / module

        module_status[module] = module_path.exists()

    return module_status


def generate_report(
    scan_results, total_files, files_with_issues, pi_connectivity, module_status
):
    """Generate comprehensive integrity report"""
    report_data = {
        "timestamp": datetime.now(UTC).isoformat(),
        "scan_summary": {
            "total_files_scanned": total_files,
            "files_with_issues": files_with_issues,
            "integrity_score": (
                round((total_files - files_with_issues) / total_files * 100, 2)
                if total_files > 0
                else 0
            ),
        },
        "file_issues": scan_results,
        "pi_cluster_connectivity": pi_connectivity,
        "critical_modules_status": module_status,
        "repair_directory": str(FIX_DIR),
        "recommendations": [],
    }

    # Generate recommendations
    if files_with_issues > 0:
        report_data["recommendations"].append(
            "Review and replace corrupted files from repairs/ directory"
        )

    if not all(pi_connectivity.values()):
        report_data["recommendations"].append(
            "Check Raspberry Pi cluster network connectivity"
        )

    if not all(module_status.values()):
        report_data["recommendations"].append("Restore missing critical EQ12 modules")

    # Save report
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

    return report_data


def main():
    """Main execution function"""
    print("=" * 60)
    safe_print("EQ12 SYSTEM INTEGRITY VALIDATOR v1.0", "INIT")
    safe_print("ASCII-SAFE CORRUPTION DETECTION AND REPAIR", "INIT")
    print("=" * 60)

    # Ensure directories exist
    ROOT.mkdir(exist_ok=True)
    (ROOT / "logs").mkdir(exist_ok=True)
    FIX_DIR.mkdir(exist_ok=True)

    # Run comprehensive scan
    scan_results, total_files, files_with_issues = scan_all_files()

    # Check infrastructure
    pi_connectivity = check_pi_cluster()
    module_status = check_critical_modules()

    # Generate report
    report = generate_report(
        scan_results, total_files, files_with_issues, pi_connectivity, module_status
    )

    # Display summary
    print("\n" + "=" * 60)
    safe_print("INTEGRITY SCAN COMPLETE", "SUMMARY")
    print("=" * 60)
    safe_print(f"Files scanned: {total_files}")
    safe_print(f"Files with issues: {files_with_issues}")
    safe_print(f"Integrity score: {report['scan_summary']['integrity_score']}%")
    safe_print(
        f"Pi cluster nodes online: {sum(pi_connectivity.values())}/{len(pi_connectivity)}"
    )
    safe_print(
        f"Critical modules found: {sum(module_status.values())}/{len(module_status)}"
    )

    if files_with_issues > 0:
        safe_print(f"Repaired files available in: {FIX_DIR}")

    safe_print(f"Full report saved to: {REPORT}")

    # Exit with appropriate code
    if files_with_issues > 0 or not all(module_status.values()):
        safe_print("System requires attention - some issues detected", "WARNING")
        return 1
    else:
        safe_print("System integrity validated - all checks passed", "SUCCESS")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        safe_print("Scan interrupted by user", "INFO")
        sys.exit(130)
    except Exception as e:
        safe_print(f"Unexpected error: {ascii_clean(str(e))}", "ERROR")
        sys.exit(1)
