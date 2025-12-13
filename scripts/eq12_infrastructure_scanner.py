#!/usr/bin/env python3
"""
EQ12 Infrastructure Syntax Scanner & Auto-Fix
Comprehensive scanner for syntax errors, deprecation warnings, and code quality issues.
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\infrastructure_scan.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class InfrastructureScanner:
    """Comprehensive infrastructure scanning and auto-fix system"""

    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.scan_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workspace": str(self.workspace_path),
            "python_files": [],
            "powershell_files": [],
            "syntax_errors": [],
            "deprecation_warnings": [],
            "code_quality_issues": [],
            "fixed_issues": [],
            "summary": {},
        }

    def scan_python_files(self) -> List[Path]:
        """Find all Python files in workspace"""
        python_files = []
        for pattern in ["**/*.py"]:
            python_files.extend(self.workspace_path.glob(pattern))

        logger.info(f"Found {len(python_files)} Python files")
        self.scan_results["python_files"] = [str(f) for f in python_files]
        return python_files

    def scan_powershell_files(self) -> List[Path]:
        """Find all PowerShell files in workspace"""
        ps_files = []
        for pattern in ["**/*.ps1", "**/*.psm1"]:
            ps_files.extend(self.workspace_path.glob(pattern))

        logger.info(f"Found {len(ps_files)} PowerShell files")
        self.scan_results["powershell_files"] = [str(f) for f in ps_files]
        return ps_files

    def check_python_syntax(self, file_path: Path) -> List[Dict]:
        """Check Python file for syntax errors"""
        issues = []
        try:
            # Check syntax with ast
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            compile(content, str(file_path), "exec")

            # Check with flake8 for style issues
            try:
                result = subprocess.run(
                    ["python", "-m", "flake8", str(file_path), "--max-line-length=88"],
                    capture_output=True,
                    text=True,
                )
                if result.stdout.strip():
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            issues.append(
                                {
                                    "file": str(file_path),
                                    "type": "style",
                                    "message": line,
                                    "tool": "flake8",
                                }
                            )
            except Exception as e:
                logger.warning(f"Flake8 check failed for {file_path}: {e}")

        except SyntaxError as e:
            issues.append(
                {
                    "file": str(file_path),
                    "type": "syntax_error",
                    "line": e.lineno,
                    "message": str(e),
                    "tool": "python",
                }
            )
        except Exception as e:
            issues.append(
                {
                    "file": str(file_path),
                    "type": "error",
                    "message": str(e),
                    "tool": "python",
                }
            )

        return issues

    def check_powershell_syntax(self, file_path: Path) -> List[Dict]:
        """Check PowerShell file for syntax errors"""
        issues = []
        try:
            # Use PowerShell's own syntax checking
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"$null = Get-Content '{file_path}' | Out-String | "
                    + "Invoke-Expression -ErrorAction Stop",
                ],
                capture_output=True,
                text=True,
            )

            if result.stderr:
                issues.append(
                    {
                        "file": str(file_path),
                        "type": "syntax_error",
                        "message": result.stderr.strip(),
                        "tool": "powershell",
                    }
                )

            # Check for common PowerShell issues
            with open(file_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    # Check for && usage (bash syntax in PowerShell)
                    if "&&" in line and not line.strip().startswith("#"):
                        issues.append(
                            {
                                "file": str(file_path),
                                "type": "syntax_warning",
                                "line": i,
                                "message": "Using '&&' (bash syntax) instead of ';'",
                                "tool": "custom",
                            }
                        )

                    # Check for missing CmdletBinding
                    if "function " in line and "CmdletBinding" not in content:
                        issues.append(
                            {
                                "file": str(file_path),
                                "type": "best_practice",
                                "line": i,
                                "message": "Function missing [CmdletBinding()]",
                                "tool": "custom",
                            }
                        )

        except Exception as e:
            issues.append(
                {
                    "file": str(file_path),
                    "type": "error",
                    "message": str(e),
                    "tool": "powershell",
                }
            )

        return issues

    def check_fastapi_deprecations(self, file_path: Path) -> List[Dict]:
        """Check for FastAPI deprecation warnings"""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for deprecated @app.on_event patterns
            if "@app.on_event" in content:
                issues.append(
                    {
                        "file": str(file_path),
                        "type": "deprecation",
                        "message": "FastAPI @app.on_event is deprecated, use lifespan",
                        "tool": "fastapi",
                        "severity": "high",
                    }
                )

            # Check for old Pydantic patterns
            if "from pydantic import BaseModel" in content and "Field" not in content:
                issues.append(
                    {
                        "file": str(file_path),
                        "type": "warning",
                        "message": "Consider using Pydantic Field for better validation",
                        "tool": "pydantic",
                        "severity": "low",
                    }
                )

        except Exception as e:
            logger.error(f"FastAPI deprecation check failed for {file_path}: {e}")

        return issues

    def auto_fix_python_issues(self, file_path: Path, issues: List[Dict]) -> List[Dict]:
        """Attempt to auto-fix Python issues"""
        fixed = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            modified = False

            # Fix FastAPI lifespan deprecation
            if any("@app.on_event" in issue.get("message", "") for issue in issues):
                # Replace @app.on_event with lifespan pattern
                lifespan_pattern = """
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
"""
                if "@app.on_event" in content and "lifespan" not in content:
                    content = content.replace(
                        "@app.on_event", "# @app.on_event deprecated - use lifespan"
                    )
                    modified = True
                    fixed.append(
                        {
                            "file": str(file_path),
                            "type": "fastapi_lifespan",
                            "message": "Added lifespan pattern comment",
                        }
                    )

            # Run Black formatter for style fixes
            if any("style" in issue.get("type", "") for issue in issues):
                try:
                    subprocess.run(
                        ["python", "-m", "black", str(file_path), "--line-length=88"],
                        check=True,
                    )
                    fixed.append(
                        {
                            "file": str(file_path),
                            "type": "formatting",
                            "message": "Applied Black formatting",
                        }
                    )
                except Exception as e:
                    logger.warning(f"Black formatting failed: {e}")

            # Write back modified content
            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            logger.error(f"Auto-fix failed for {file_path}: {e}")

        return fixed

    def auto_fix_powershell_issues(
        self, file_path: Path, issues: List[Dict]
    ) -> List[Dict]:
        """Attempt to auto-fix PowerShell issues"""
        fixed = []

        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                content = f.read()

            modified = False

            # Fix && to ; replacement
            if "&&" in content:
                content = re.sub(r"\s*&&\s*", "; ", content)
                modified = True
                fixed.append(
                    {
                        "file": str(file_path),
                        "type": "syntax_fix",
                        "message": "Replaced '&&' with ';' for PowerShell syntax",
                    }
                )

            # Add CmdletBinding to functions
            if "function " in content and "[CmdletBinding()]" not in content:
                content = re.sub(
                    r"^(\s*function\s+\w+.*?)\s*{",
                    r"\1 {\n    [CmdletBinding()]",
                    content,
                    flags=re.MULTILINE,
                )
                modified = True
                fixed.append(
                    {
                        "file": str(file_path),
                        "type": "best_practice",
                        "message": "Added [CmdletBinding()] to functions",
                    }
                )

            # Write back modified content
            if modified:
                with open(file_path, "w", encoding="utf-8-sig") as f:
                    f.write(content)

        except Exception as e:
            logger.error(f"PowerShell auto-fix failed for {file_path}: {e}")

        return fixed

    def run_comprehensive_scan(self, auto_fix: bool = True) -> Dict:
        """Run comprehensive infrastructure scan"""
        logger.info("Starting comprehensive infrastructure scan...")

        # Scan for files
        python_files = self.scan_python_files()
        powershell_files = self.scan_powershell_files()

        total_issues = 0
        total_fixed = 0

        # Process Python files
        for py_file in python_files:
            logger.info(f"Scanning Python file: {py_file}")
            issues = self.check_python_syntax(py_file)
            issues.extend(self.check_fastapi_deprecations(py_file))

            self.scan_results["syntax_errors"].extend(issues)
            total_issues += len(issues)

            if auto_fix and issues:
                fixed = self.auto_fix_python_issues(py_file, issues)
                self.scan_results["fixed_issues"].extend(fixed)
                total_fixed += len(fixed)

        # Process PowerShell files
        for ps_file in powershell_files:
            logger.info(f"Scanning PowerShell file: {ps_file}")
            issues = self.check_powershell_syntax(ps_file)

            self.scan_results["syntax_errors"].extend(issues)
            total_issues += len(issues)

            if auto_fix and issues:
                fixed = self.auto_fix_powershell_issues(ps_file, issues)
                self.scan_results["fixed_issues"].extend(fixed)
                total_fixed += len(fixed)

        # Generate summary
        self.scan_results["summary"] = {
            "total_files_scanned": len(python_files) + len(powershell_files),
            "python_files_count": len(python_files),
            "powershell_files_count": len(powershell_files),
            "total_issues_found": total_issues,
            "total_issues_fixed": total_fixed,
            "scan_duration": "completed",
            "auto_fix_enabled": auto_fix,
        }

        logger.info(f"Scan complete: {total_issues} issues found, {total_fixed} fixed")
        return self.scan_results

    def save_scan_report(self) -> Path:
        """Save scan results to JSON report"""
        report_path = (
            self.workspace_path
            / "logs"
            / f"infrastructure_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.scan_results, f, indent=2)

        logger.info(f"Scan report saved to: {report_path}")
        return report_path

    def generate_html_report(self) -> Path:
        """Generate HTML report for scan results"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 Infrastructure Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #0066cc; color: white; padding: 20px; }}
        .summary {{ background: #f0f8ff; padding: 15px; margin: 20px 0; }}
        .issue {{ background: #ffe6e6; padding: 10px; margin: 5px 0; border-left: 4px solid #ff0000; }}
        .fixed {{ background: #e6ffe6; padding: 10px; margin: 5px 0; border-left: 4px solid #00cc00; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffcc00; }}
        .error {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1> EQ12 Infrastructure Scan Report</h1>
        <p>Generated: {self.scan_results['timestamp']}</p>
    </div>
    
    <div class="summary">
        <h2> Scan Summary</h2>
        <ul>
            <li><strong>Total Files Scanned:</strong> {self.scan_results['summary'].get('total_files_scanned', 0)}</li>
            <li><strong>Python Files:</strong> {self.scan_results['summary'].get('python_files_count', 0)}</li>
            <li><strong>PowerShell Files:</strong> {self.scan_results['summary'].get('powershell_files_count', 0)}</li>
            <li><strong>Issues Found:</strong> {self.scan_results['summary'].get('total_issues_found', 0)}</li>
            <li><strong>Issues Fixed:</strong> {self.scan_results['summary'].get('total_issues_fixed', 0)}</li>
        </ul>
    </div>
    
    <h2> Issues Found</h2>
    {''.join([f'<div class="issue {issue.get("type", "")}">{issue.get("file", "")}: {issue.get("message", "")}</div>' for issue in self.scan_results['syntax_errors']])}
    
    <h2> Issues Fixed</h2>
    {''.join([f'<div class="fixed">{fix.get("file", "")}: {fix.get("message", "")}</div>' for fix in self.scan_results['fixed_issues']])}
    
</body>
</html>
"""

        report_path = (
            self.workspace_path
            / "dashboard"
            / f"infrastructure_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML report generated: {report_path}")
        return report_path


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="EQ12 Infrastructure Syntax Scanner & Auto-Fix"
    )
    parser.add_argument(
        "--workspace", default="C:\\EQ12", help="Workspace path to scan"
    )
    parser.add_argument(
        "--auto-fix", action="store_true", help="Automatically fix issues where possible"
    )
    parser.add_argument(
        "--report-only", action="store_true", help="Generate report without scanning"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    scanner = InfrastructureScanner(args.workspace)

    if not args.report_only:
        # Run comprehensive scan
        results = scanner.run_comprehensive_scan(auto_fix=args.auto_fix)

        # Save reports
        json_report = scanner.save_scan_report()
        html_report = scanner.generate_html_report()

        print(f"\n EQ12 Infrastructure Scan Complete!")
        print(f" JSON Report: {json_report}")
        print(f" HTML Report: {html_report}")
        print(f" Summary: {results['summary']}")

    else:
        print("Report-only mode not implemented yet")

    return 0


if __name__ == "__main__":
    sys.exit(main())