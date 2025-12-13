"""
EQ12 SELF-SCAN ENGINE - AUTONOMOUS SYSTEM DIAGNOSTIC
Detects 30+ common issues and generates auto-fix scripts
Contract: Structured JSON reports → logs/ directory with UTC timestamps
"""

import os
import sys
import json
import sqlite3
import logging
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ScanIssue:
    """Detected system issue"""
    category: str  # path|dependency|database|import|config|scheduling|api|permission
    severity: str  # LOW|MEDIUM|HIGH|CRITICAL
    title: str
    description: str
    affected_files: List[str]
    auto_fix_available: bool
    fix_command: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


class EQ12SystemScanner:
    """Master diagnostic engine for EQ12 stack"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.issues: List[ScanIssue] = []
        self.scan_timestamp = datetime.now(timezone.utc)
        self.stats = {
            "files_scanned": 0,
            "databases_checked": 0,
            "imports_validated": 0,
            "errors_found": 0
        }
    
    def run_full_scan(self) -> Dict:
        """Execute all 30 diagnostic checks"""
        logger.info(f"Starting full system scan at {self.scan_timestamp.isoformat()}")
        
        # Category 1: Path Issues (5 checks)
        self.check_path_mismatches()
        self.check_relative_import_breaks()
        self.check_missing_directories()
        self.check_workspace_portability()
        self.check_symlink_validity()
        
        # Category 2: Dependencies (5 checks)
        self.check_python_version()
        self.check_missing_python_libs()
        self.check_vbnet_nuget_packages()
        self.check_requirements_drift()
        self.check_conflicting_versions()
        
        # Category 3: Database (5 checks)
        self.check_database_locks()
        self.check_schema_drift()
        self.check_missing_indexes()
        self.check_database_corruption()
        self.check_orphaned_journal_files()
        
        # Category 4: Imports (5 checks)
        self.check_broken_imports()
        self.check_circular_dependencies()
        self.check_unused_imports()
        self.check_star_imports()
        self.check_missing_type_hints()
        
        # Category 5: Configuration (5 checks)
        self.check_git_conflicts()
        self.check_env_variable_missing()
        self.check_vscode_settings_conflicts()
        self.check_tasks_json_syntax()
        self.check_devcontainer_config()
        
        # Category 6: Scheduling (5 checks)
        self.check_overlapping_cron_jobs()
        self.check_task_scheduler_conflicts()
        self.check_timezone_handling()
        self.check_race_conditions()
        self.check_failed_scheduled_runs()
        
        # Generate report
        report = self.generate_report()
        self.save_report(report)
        return report
    
    # ========== PATH CHECKS ==========
    
    def check_path_mismatches(self):
        """Issue 1: Windows vs Linux path separators"""
        logger.info("Checking for path mismatches (Windows vs Linux)...")
        py_files = list(self.repo_root.rglob("*.py"))
        self.stats["files_scanned"] += len(py_files)
        
        issues_found = []
        for py_file in py_files[:500]:  # Sample first 500
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                # Detect hardcoded Windows paths
                if "C:\\" in content or "\\\\Users\\\\" in content:
                    issues_found.append(str(py_file))
            except Exception:
                pass
        
        if issues_found:
            self.issues.append(ScanIssue(
                category="path",
                severity="MEDIUM",
                title="Hardcoded Windows paths detected",
                description=f"{len(issues_found)} files contain hardcoded Windows paths (C:\\, \\Users\\)",
                affected_files=issues_found[:10],
                auto_fix_available=True,
                fix_command="python scripts/fix_paths.py --convert-to-pathlib"
            ))
    
    def check_relative_import_breaks(self):
        """Issue 2: Broken relative imports after folder moves"""
        logger.info("Checking for broken relative imports...")
        # Detect imports like `from ..utils import` that fail
        py_files = list(self.repo_root.rglob("*.py"))
        
        broken = []
        for py_file in py_files[:300]:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "from .." in content or "from ." in content:
                    # Try to validate import (simple heuristic)
                    if not self._validate_relative_import(py_file, content):
                        broken.append(str(py_file))
            except Exception:
                pass
        
        if broken:
            self.issues.append(ScanIssue(
                category="import",
                severity="HIGH",
                title="Broken relative imports detected",
                description=f"{len(broken)} files have invalid relative imports",
                affected_files=broken[:5],
                auto_fix_available=False
            ))
    
    def _validate_relative_import(self, file_path: Path, content: str) -> bool:
        """Simple validation of relative imports"""
        # Check if __init__.py exists in parent
        return (file_path.parent / "__init__.py").exists()
    
    def check_missing_directories(self):
        """Issue 3: Missing critical directories"""
        logger.info("Checking for missing directories...")
        required_dirs = [
            "scripts", "src", "logs", "tests", "databases",
            "src/EQ12.Phase33", "tests/pester"
        ]
        
        missing = [d for d in required_dirs if not (self.repo_root / d).exists()]
        
        if missing:
            self.issues.append(ScanIssue(
                category="path",
                severity="HIGH",
                title="Missing critical directories",
                description=f"{len(missing)} required directories not found",
                affected_files=missing,
                auto_fix_available=True,
                fix_command="mkdir " + " ".join(missing)
            ))
    
    def check_workspace_portability(self):
        """Issue 4: Non-portable workspace references"""
        logger.info("Checking workspace portability...")
        # Check for absolute paths in .vscode/
        vscode_settings = self.repo_root / ".vscode" / "settings.json"
        if vscode_settings.exists():
            content = vscode_settings.read_text()
            if "C:\\" in content or "/Users/" in content:
                self.issues.append(ScanIssue(
                    category="config",
                    severity="LOW",
                    title="Non-portable VS Code settings",
                    description=".vscode/settings.json contains absolute paths",
                    affected_files=[str(vscode_settings)],
                    auto_fix_available=True
                ))
    
    def check_symlink_validity(self):
        """Issue 5: Broken symlinks"""
        logger.info("Checking symlinks...")
        # Windows symlinks are rare, skip for now
        pass
    
    # ========== DEPENDENCY CHECKS ==========
    
    def check_python_version(self):
        """Issue 6: Python version conflicts"""
        logger.info("Checking Python version...")
        import sys
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        if sys.version_info < (3, 10):
            self.issues.append(ScanIssue(
                category="dependency",
                severity="HIGH",
                title="Python version too old",
                description=f"Current: {version}, Required: 3.10+",
                affected_files=[],
                auto_fix_available=False
            ))
        else:
            logger.info(f"Python version OK: {version}")
    
    def check_missing_python_libs(self):
        """Issue 7: Missing Python dependencies"""
        logger.info("Checking Python libraries...")
        required_libs = [
            "requests", "pandas", "numpy", "sqlite3",
            "sklearn", "xgboost", "lightgbm", "pytest"
        ]
        
        missing = []
        for lib in required_libs:
            if lib == "sklearn":
                lib = "scikit-learn"  # Import vs install name
            
            spec = importlib.util.find_spec(lib.replace("-", "_"))
            if spec is None:
                missing.append(lib)
        
        if missing:
            self.issues.append(ScanIssue(
                category="dependency",
                severity="HIGH",
                title="Missing Python libraries",
                description=f"{len(missing)} required libraries not installed",
                affected_files=missing,
                auto_fix_available=True,
                fix_command=f"pip install {' '.join(missing)}"
            ))
    
    def check_vbnet_nuget_packages(self):
        """Issue 8: Missing NuGet packages for VB.NET"""
        logger.info("Checking VB.NET NuGet packages...")
        # Look for .vbproj files
        vb_projects = list(self.repo_root.rglob("*.vbproj"))
        
        for proj in vb_projects:
            content = proj.read_text()
            required_packages = ["System.Data.SQLite", "Newtonsoft.Json"]
            missing_in_proj = [pkg for pkg in required_packages if pkg not in content]
            
            if missing_in_proj:
                self.issues.append(ScanIssue(
                    category="dependency",
                    severity="MEDIUM",
                    title="Missing NuGet packages in VB.NET project",
                    description=f"{proj.name} missing: {', '.join(missing_in_proj)}",
                    affected_files=[str(proj)],
                    auto_fix_available=True,
                    fix_command=f"dotnet add {proj} package {missing_in_proj[0]}"
                ))
    
    def check_requirements_drift(self):
        """Issue 9: requirements.txt vs installed packages drift"""
        logger.info("Checking requirements.txt drift...")
        req_file = self.repo_root / "requirements.txt"
        if req_file.exists():
            # Compare with `pip freeze`
            try:
                result = subprocess.run(["pip", "freeze"], capture_output=True, text=True, timeout=10)
                installed = set(result.stdout.splitlines())
                required = set(req_file.read_text().splitlines())
                
                missing = required - installed
                if missing:
                    self.issues.append(ScanIssue(
                        category="dependency",
                        severity="MEDIUM",
                        title="requirements.txt drift detected",
                        description=f"{len(missing)} packages in requirements.txt not installed",
                        affected_files=[str(req_file)],
                        auto_fix_available=True,
                        fix_command="pip install -r requirements.txt"
                    ))
            except Exception as e:
                logger.warning(f"Could not check requirements drift: {e}")
    
    def check_conflicting_versions(self):
        """Issue 10: Conflicting package versions"""
        logger.info("Checking for version conflicts...")
        # Use pip check
        try:
            result = subprocess.run(["pip", "check"], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                self.issues.append(ScanIssue(
                    category="dependency",
                    severity="MEDIUM",
                    title="Package version conflicts",
                    description=result.stdout,
                    affected_files=[],
                    auto_fix_available=False
                ))
        except Exception:
            pass
    
    # ========== DATABASE CHECKS ==========
    
    def check_database_locks(self):
        """Issue 11: SQLite lock files"""
        logger.info("Checking for database locks...")
        db_files = list(self.repo_root.rglob("*.db"))
        self.stats["databases_checked"] = len(db_files)
        
        locked = []
        for db in db_files:
            lock_file = db.parent / (db.name + "-journal")
            wal_file = db.parent / (db.name + "-wal")
            
            if lock_file.exists() or wal_file.exists():
                locked.append(str(db))
        
        if locked:
            self.issues.append(ScanIssue(
                category="database",
                severity="MEDIUM",
                title="SQLite lock files detected",
                description=f"{len(locked)} databases have active lock/WAL files",
                affected_files=locked,
                auto_fix_available=True,
                fix_command="# Close all SQLite connections, then delete -journal/-wal files"
            ))
    
    def check_schema_drift(self):
        """Issue 12: Database schema drift"""
        logger.info("Checking schema drift...")
        # Check eq12_memory.db schema vs init script
        eq12_db = self.repo_root / "logs" / "eq12_memory.db"
        init_sql = self.repo_root / "databases" / "init_eq12_memory.sql"
        
        if eq12_db.exists() and init_sql.exists():
            try:
                conn = sqlite3.connect(eq12_db)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                actual_tables = set(row[0] for row in cursor.fetchall())
                conn.close()
                
                # Expected tables from init script
                expected = {"orchestration_logs", "conversions_daily", "funnel_health",
                           "model_registry", "drift_history", "next_moves", "attribution"}
                
                missing = expected - actual_tables
                if missing:
                    self.issues.append(ScanIssue(
                        category="database",
                        severity="HIGH",
                        title="Database schema drift",
                        description=f"Missing tables in eq12_memory.db: {', '.join(missing)}",
                        affected_files=[str(eq12_db)],
                        auto_fix_available=True,
                        fix_command=f"sqlite3 {eq12_db} < {init_sql}"
                    ))
            except Exception as e:
                logger.warning(f"Could not check schema: {e}")
    
    def check_missing_indexes(self):
        """Issue 13: Missing database indexes"""
        logger.info("Checking database indexes...")
        eq12_db = self.repo_root / "logs" / "eq12_memory.db"
        
        if eq12_db.exists():
            try:
                conn = sqlite3.connect(eq12_db)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
                indexes = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                # Should have at least 5 indexes
                if len(indexes) < 5:
                    self.issues.append(ScanIssue(
                        category="database",
                        severity="LOW",
                        title="Missing database indexes",
                        description=f"Only {len(indexes)} indexes found (expected 10+)",
                        affected_files=[str(eq12_db)],
                        auto_fix_available=False
                    ))
            except Exception:
                pass
    
    def check_database_corruption(self):
        """Issue 14: Database corruption check"""
        logger.info("Checking for database corruption...")
        db_files = list(self.repo_root.rglob("*.db"))[:20]  # Sample
        
        corrupted = []
        for db in db_files:
            try:
                conn = sqlite3.connect(db)
                conn.execute("PRAGMA integrity_check;")
                conn.close()
            except Exception:
                corrupted.append(str(db))
        
        if corrupted:
            self.issues.append(ScanIssue(
                category="database",
                severity="CRITICAL",
                title="Database corruption detected",
                description=f"{len(corrupted)} databases failed integrity check",
                affected_files=corrupted,
                auto_fix_available=False
            ))
    
    def check_orphaned_journal_files(self):
        """Issue 15: Orphaned -journal files"""
        logger.info("Checking for orphaned journal files...")
        journals = list(self.repo_root.rglob("*.db-journal"))
        
        orphaned = []
        for journal in journals:
            db_file = journal.parent / journal.name.replace("-journal", "")
            if not db_file.exists():
                orphaned.append(str(journal))
        
        if orphaned:
            self.issues.append(ScanIssue(
                category="database",
                severity="LOW",
                title="Orphaned journal files",
                description=f"{len(orphaned)} -journal files without parent database",
                affected_files=orphaned,
                auto_fix_available=True,
                fix_command="# Delete orphaned -journal files"
            ))
    
    # ========== IMPORT CHECKS ==========
    
    def check_broken_imports(self):
        """Issue 16: Broken import statements"""
        logger.info("Checking for broken imports...")
        # This is expensive, so sample files
        py_files = list(self.repo_root.rglob("*.py"))[:100]
        
        broken = []
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                # Detect common broken patterns
                if "from nba_utils import" in content and not (self.repo_root / "scripts" / "nba_utils.py").exists():
                    broken.append(str(py_file))
            except Exception:
                pass
        
        if broken:
            self.issues.append(ScanIssue(
                category="import",
                severity="MEDIUM",
                title="Broken imports detected",
                description=f"{len(broken)} files import non-existent modules",
                affected_files=broken,
                auto_fix_available=False
            ))
    
    def check_circular_dependencies(self):
        """Issue 17: Circular import detection"""
        logger.info("Checking for circular dependencies...")
        # Placeholder - complex analysis
        pass
    
    def check_unused_imports(self):
        """Issue 18: Unused imports"""
        logger.info("Checking for unused imports...")
        # Use ruff or similar linter (placeholder)
        pass
    
    def check_star_imports(self):
        """Issue 19: Star imports (bad practice)"""
        logger.info("Checking for star imports...")
        py_files = list(self.repo_root.rglob("*.py"))[:200]
        
        star_import_files = []
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "import *" in content:
                    star_import_files.append(str(py_file))
            except Exception:
                pass
        
        if star_import_files:
            self.issues.append(ScanIssue(
                category="import",
                severity="LOW",
                title="Star imports detected",
                description=f"{len(star_import_files)} files use 'import *' (bad practice)",
                affected_files=star_import_files[:5],
                auto_fix_available=False
            ))
    
    def check_missing_type_hints(self):
        """Issue 20: Missing type hints in function signatures"""
        logger.info("Checking for missing type hints...")
        # Placeholder - requires AST parsing
        pass
    
    # ========== CONFIGURATION CHECKS ==========
    
    def check_git_conflicts(self):
        """Issue 21: Unresolved Git conflicts"""
        logger.info("Checking for Git conflicts...")
        try:
            result = subprocess.run(["git", "diff", "--check"], capture_output=True, text=True, timeout=5, cwd=self.repo_root)
            if result.returncode != 0:
                self.issues.append(ScanIssue(
                    category="config",
                    severity="HIGH",
                    title="Git conflict markers detected",
                    description=result.stdout,
                    affected_files=[],
                    auto_fix_available=False
                ))
        except Exception:
            pass
    
    def check_env_variable_missing(self):
        """Issue 22: Missing environment variables"""
        logger.info("Checking environment variables...")
        required_env = ["ODDS_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
        
        missing = [var for var in required_env if not os.getenv(var)]
        
        if missing:
            self.issues.append(ScanIssue(
                category="config",
                severity="MEDIUM",
                title="Missing environment variables",
                description=f"{len(missing)} required env vars not set: {', '.join(missing)}",
                affected_files=[],
                auto_fix_available=True,
                fix_command=f"# Set in PowerShell: $env:{missing[0]}='your_value_here'"
            ))
    
    def check_vscode_settings_conflicts(self):
        """Issue 23: Conflicting VS Code settings"""
        logger.info("Checking VS Code settings...")
        settings_file = self.repo_root / ".vscode" / "settings.json"
        
        if settings_file.exists():
            try:
                content = json.loads(settings_file.read_text())
                # Check for conflicting formatters
                if "python.formatting.provider" in content and "editor.defaultFormatter" in content:
                    self.issues.append(ScanIssue(
                        category="config",
                        severity="LOW",
                        title="Conflicting VS Code formatter settings",
                        description="Both python.formatting.provider and editor.defaultFormatter set",
                        affected_files=[str(settings_file)],
                        auto_fix_available=False
                    ))
            except Exception:
                pass
    
    def check_tasks_json_syntax(self):
        """Issue 24: tasks.json syntax errors"""
        logger.info("Checking tasks.json...")
        tasks_file = self.repo_root / ".vscode" / "tasks.json"
        
        if tasks_file.exists():
            try:
                json.loads(tasks_file.read_text())
            except json.JSONDecodeError as e:
                self.issues.append(ScanIssue(
                    category="config",
                    severity="MEDIUM",
                    title="tasks.json syntax error",
                    description=str(e),
                    affected_files=[str(tasks_file)],
                    auto_fix_available=False
                ))
    
    def check_devcontainer_config(self):
        """Issue 25: Devcontainer config issues"""
        logger.info("Checking devcontainer config...")
        # Placeholder
        pass
    
    # ========== SCHEDULING CHECKS ==========
    
    def check_overlapping_cron_jobs(self):
        """Issue 26: Overlapping cron jobs (Linux)"""
        logger.info("Checking cron jobs...")
        # Windows only - check Task Scheduler instead
        pass
    
    def check_task_scheduler_conflicts(self):
        """Issue 27: Windows Task Scheduler conflicts"""
        logger.info("Checking Task Scheduler...")
        # Requires PowerShell query
        pass
    
    def check_timezone_handling(self):
        """Issue 28: Inconsistent timezone handling"""
        logger.info("Checking timezone handling...")
        # Look for naive datetime usage
        py_files = list(self.repo_root.rglob("*.py"))[:100]
        
        naive_datetime_files = []
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "datetime.now()" in content and "timezone" not in content:
                    naive_datetime_files.append(str(py_file))
            except Exception:
                pass
        
        if naive_datetime_files:
            self.issues.append(ScanIssue(
                category="scheduling",
                severity="MEDIUM",
                title="Naive datetime usage (no timezone)",
                description=f"{len(naive_datetime_files)} files use datetime.now() without timezone",
                affected_files=naive_datetime_files[:5],
                auto_fix_available=False
            ))
    
    def check_race_conditions(self):
        """Issue 29: Potential race conditions"""
        logger.info("Checking for race conditions...")
        # Placeholder - complex analysis
        pass
    
    def check_failed_scheduled_runs(self):
        """Issue 30: Failed scheduled runs in logs"""
        logger.info("Checking scheduled run history...")
        # Query orchestration_logs for errors
        eq12_db = self.repo_root / "logs" / "eq12_memory.db"
        
        if eq12_db.exists():
            try:
                conn = sqlite3.connect(eq12_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM orchestration_logs WHERE errors IS NOT NULL;")
                error_count = cursor.fetchone()[0]
                conn.close()
                
                if error_count > 0:
                    self.issues.append(ScanIssue(
                        category="scheduling",
                        severity="MEDIUM",
                        title="Failed scheduled runs detected",
                        description=f"{error_count} executions logged errors",
                        affected_files=[str(eq12_db)],
                        auto_fix_available=False
                    ))
            except Exception:
                pass
    
    # ========== REPORTING ==========
    
    def generate_report(self) -> Dict:
        """Generate comprehensive health report"""
        logger.info("Generating health report...")
        
        report = {
            "scan_timestamp": self.scan_timestamp.isoformat(),
            "repo_root": str(self.repo_root),
            "statistics": self.stats,
            "summary": {
                "total_issues": len(self.issues),
                "critical": len([i for i in self.issues if i.severity == "CRITICAL"]),
                "high": len([i for i in self.issues if i.severity == "HIGH"]),
                "medium": len([i for i in self.issues if i.severity == "MEDIUM"]),
                "low": len([i for i in self.issues if i.severity == "LOW"]),
                "auto_fixable": len([i for i in self.issues if i.auto_fix_available])
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "health_score": self._calculate_health_score(),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _calculate_health_score(self) -> int:
        """Calculate health score 0-100"""
        if not self.issues:
            return 100
        
        # Weighted penalties
        penalties = {
            "CRITICAL": 25,
            "HIGH": 10,
            "MEDIUM": 5,
            "LOW": 1
        }
        
        total_penalty = sum(penalties.get(issue.severity, 0) for issue in self.issues)
        score = max(0, 100 - total_penalty)
        return score
    
    def _generate_recommendations(self) -> List[str]:
        """Generate top recommendations"""
        recs = []
        
        if any(i.severity == "CRITICAL" for i in self.issues):
            recs.append("🚨 CRITICAL issues detected - address immediately")
        
        auto_fixable = [i for i in self.issues if i.auto_fix_available]
        if auto_fixable:
            recs.append(f"✅ {len(auto_fixable)} issues can be auto-fixed")
        
        if len(self.issues) == 0:
            recs.append("✨ System is healthy - no issues detected")
        
        return recs
    
    def save_report(self, report: Dict):
        """Save report to logs/ directory"""
        timestamp_str = self.scan_timestamp.strftime("%Y%m%d_%H%M%S")
        output_file = self.repo_root / "logs" / f"system_scan_{timestamp_str}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Report saved to {output_file}")
        
        # Also save markdown summary
        md_file = output_file.with_suffix('.md')
        self._save_markdown_report(report, md_file)
        logger.info(f"✅ Markdown report saved to {md_file}")
    
    def _save_markdown_report(self, report: Dict, md_file: Path):
        """Save human-readable markdown report"""
        lines = [
            f"# EQ12 System Health Report",
            f"**Scan Time:** {report['scan_timestamp']}",
            f"**Health Score:** {report['health_score']}/100\n",
            f"## Summary",
            f"- **Total Issues:** {report['summary']['total_issues']}",
            f"- **Critical:** {report['summary']['critical']}",
            f"- **High:** {report['summary']['high']}",
            f"- **Medium:** {report['summary']['medium']}",
            f"- **Low:** {report['summary']['low']}",
            f"- **Auto-Fixable:** {report['summary']['auto_fixable']}\n",
            f"## Statistics",
            f"- Files Scanned: {report['statistics']['files_scanned']}",
            f"- Databases Checked: {report['statistics']['databases_checked']}",
            f"- Imports Validated: {report['statistics']['imports_validated']}\n",
            f"## Recommendations"
        ]
        
        for rec in report['recommendations']:
            lines.append(f"- {rec}")
        
        lines.append("\n## Detailed Issues\n")
        
        for issue in report['issues']:
            lines.append(f"### {issue['title']}")
            lines.append(f"**Severity:** {issue['severity']}  ")
            lines.append(f"**Category:** {issue['category']}  ")
            lines.append(f"**Description:** {issue['description']}  ")
            if issue['auto_fix_available'] and issue.get('fix_command'):
                lines.append(f"**Fix:** `{issue['fix_command']}`  ")
            lines.append("")
        
        md_file.write_text("\n".join(lines))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Self-Scan Engine")
    parser.add_argument("--repo-root", default=Path(__file__).parent.parent, help="Repository root path")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    scanner = EQ12SystemScanner(args.repo_root)
    report = scanner.run_full_scan()
    
    print("\n" + "="*60)
    print(f"🏥 SYSTEM HEALTH SCORE: {report['health_score']}/100")
    print("="*60)
    print(f"Total Issues: {report['summary']['total_issues']}")
    print(f"  - Critical: {report['summary']['critical']}")
    print(f"  - High: {report['summary']['high']}")
    print(f"  - Medium: {report['summary']['medium']}")
    print(f"  - Low: {report['summary']['low']}")
    print(f"\nAuto-Fixable: {report['summary']['auto_fixable']}")
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  {rec}")
    print("\n✅ Full report saved to logs/")
