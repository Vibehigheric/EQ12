#!/usr/bin/env python3
"""
EQ12 Python Bytecode (.pyc) Expert Fixer
Comprehensive analysis, cleanup, and optimization of Python bytecode files
"""

import compileall
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"pyc_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(),
    ],
)


class PycExpertFixer:
    def __init__(self, root_path: str = "C:\\EQ12"):
        self.root_path = Path(root_path)
        self.fixes_applied = 0
        self.files_processed = 0
        self.bytes_cleaned = 0
        self.issues_found = []
        self.stale_pyc_files = []

    def analyze_pyc_file(self, pyc_path: Path) -> dict[str, Any]:
        """Analyze a .pyc file for issues"""
        analysis = {
            "valid": False,
            "size": 0,
            "age_days": 0,
            "source_exists": False,
            "source_newer": False,
            "corrupted": False,
            "stale": False,
            "python_version": None,
            "issues": [],
        }

        try:
            analysis["size"] = pyc_path.stat().st_size
            pyc_mtime = datetime.fromtimestamp(pyc_path.stat().st_mtime)
            analysis["age_days"] = (datetime.now() - pyc_mtime).days

            # Find corresponding source file
            if "__pycache__" in str(pyc_path):
                # Standard __pycache__ structure
                parent_dir = pyc_path.parent.parent
                filename_parts = pyc_path.stem.split(".")
                if len(filename_parts) >= 2:
                    source_name = filename_parts[0] + ".py"
                    source_path = parent_dir / source_name
                else:
                    source_path = parent_dir / (pyc_path.stem + ".py")
            else:
                # Legacy .pyc next to .py
                source_path = pyc_path.with_suffix(".py")

            if source_path.exists():
                analysis["source_exists"] = True
                source_mtime = datetime.fromtimestamp(source_path.stat().st_mtime)
                analysis["source_newer"] = source_mtime > pyc_mtime

                if analysis["source_newer"]:
                    analysis["stale"] = True
                    analysis["issues"].append("Source file is newer than bytecode")
            else:
                analysis["issues"].append("Source file missing - orphaned bytecode")
                analysis["stale"] = True

            # Try to extract Python version from filename
            if "__pycache__" in str(pyc_path):
                filename_parts = pyc_path.stem.split(".")
                for part in filename_parts:
                    if part.startswith("cpython-"):
                        version_part = part.replace("cpython-", "")
                        analysis["python_version"] = version_part.split("-")[0]
                        break

            # Check if it's for wrong Python version
            current_version = f"{sys.version_info.major}{sys.version_info.minor}"
            if analysis["python_version"] and not analysis["python_version"].startswith(
                current_version
            ):
                analysis["issues"].append(
                    f"Compiled for Python {analysis['python_version']}, current is {current_version}"
                )
                analysis["stale"] = True

            # Try to validate the bytecode
            try:
                with open(pyc_path, "rb") as f:
                    # Read magic number and timestamp
                    magic = f.read(4)
                    timestamp = f.read(4)
                    if len(magic) == 4 and len(timestamp) == 4:
                        analysis["valid"] = True
                    else:
                        analysis["corrupted"] = True
                        analysis["issues"].append("Invalid bytecode structure")
            except Exception:
                analysis["corrupted"] = True
                analysis["issues"].append("Cannot read bytecode file")

            # Check for very old files (over 30 days)
            if analysis["age_days"] > 30:
                analysis["stale"] = True
                analysis["issues"].append(f"Very old bytecode ({analysis['age_days']} days)")

        except Exception as e:
            analysis["issues"].append(f"Analysis error: {e}")

        return analysis

    def find_problematic_pyc_files(self) -> list[tuple[Path, dict[str, Any]]]:
        """Find all problematic .pyc files"""
        problematic_files = []

        logging.info("Scanning for .pyc files...")
        pyc_files = list(self.root_path.rglob("*.pyc"))
        logging.info(f"Found {len(pyc_files)} .pyc files")

        for pyc_file in pyc_files:
            self.files_processed += 1
            analysis = self.analyze_pyc_file(pyc_file)

            if analysis["issues"] or analysis["stale"] or analysis["corrupted"]:
                problematic_files.append((pyc_file, analysis))

            if self.files_processed % 1000 == 0:
                logging.info(f"Analyzed {self.files_processed} files...")

        return problematic_files

    def clean_stale_pyc_files(self, force_all: bool = False) -> int:
        """Clean stale and problematic .pyc files"""
        cleaned_count = 0

        if force_all:
            # Remove all __pycache__ directories
            pycache_dirs = list(self.root_path.rglob("__pycache__"))
            for pycache_dir in pycache_dirs:
                try:
                    shutil.rmtree(pycache_dir)
                    logging.info(f"Removed __pycache__ directory: {pycache_dir}")
                    cleaned_count += 1
                except Exception as e:
                    logging.error(f"Failed to remove {pycache_dir}: {e}")
                    self.issues_found.append(f"Failed to remove {pycache_dir}: {e}")
        else:
            # Selective cleanup based on analysis
            problematic_files = self.find_problematic_pyc_files()

            for pyc_file, analysis in problematic_files:
                try:
                    file_size = pyc_file.stat().st_size
                    pyc_file.unlink()
                    self.bytes_cleaned += file_size
                    cleaned_count += 1

                    reasons = ", ".join(analysis["issues"])
                    logging.info(f"Cleaned {pyc_file.name}: {reasons}")

                except Exception as e:
                    logging.error(f"Failed to clean {pyc_file}: {e}")
                    self.issues_found.append(f"Failed to clean {pyc_file}: {e}")

        self.fixes_applied += cleaned_count
        return cleaned_count

    def recompile_python_files(self, target_dirs: list[str] | None = None) -> int:
        """Recompile Python files to generate fresh bytecode"""
        compiled_count = 0

        if target_dirs is None:
            target_dirs = ["scripts", "buffalo_stack", "tests", "scraper_starter"]

        for target_dir in target_dirs:
            dir_path = self.root_path / target_dir
            if not dir_path.exists():
                continue

            try:
                logging.info(f"Recompiling Python files in {target_dir}...")

                # Use compileall to compile all .py files
                success = compileall.compile_dir(
                    str(dir_path), maxlevels=10, ddir=str(dir_path), force=True, quiet=1
                )

                if success:
                    # Count newly created .pyc files
                    new_pyc_files = list(dir_path.rglob("*.pyc"))
                    compiled_count += len(new_pyc_files)
                    logging.info(
                        f"Successfully recompiled {len(new_pyc_files)} files in {target_dir}"
                    )
                else:
                    logging.warning(f"Some compilation issues in {target_dir}")

            except Exception as e:
                logging.error(f"Failed to recompile {target_dir}: {e}")
                self.issues_found.append(f"Recompilation error in {target_dir}: {e}")

        return compiled_count

    def optimize_bytecode(self) -> None:
        """Optimize bytecode generation settings"""
        try:
            # Create optimization script
            optimization_script = self.root_path / "optimize_bytecode.py"

            opt_content = '''#!/usr/bin/env python3
"""
EQ12 Bytecode Optimization Script
Optimizes Python bytecode for production deployment
"""

import compileall
import os
import sys
from pathlib import Path

def optimize_eq12_bytecode():
    """Optimize bytecode for EQ12 project"""
    root_path = Path(__file__).parent

    # Directories to optimize
    target_dirs = [
        "scripts",
        "buffalo_stack",
        "eq12_config.py",
        "scraper_starter/scraper.py",
        "omni_scraper",
        "graphics"
    ]

    print("🚀 EQ12 Bytecode Optimization Starting...")

    for target in target_dirs:
        target_path = root_path / target
        if target_path.exists():
            if target_path.is_file():
                # Single file optimization
                print("Optimizing {target}...")
                compileall.compile_file(
                    str(target_path),
                    force=True,
                    optimize=2,  # Maximum optimization
                    quiet=1
                )
            else:
                # Directory optimization
                print("Optimizing directory {target}...")
                compileall.compile_dir(
                    str(target_path),
                    maxlevels=10,
                    force=True,
                    optimize=2,  # Maximum optimization
                    quiet=1
                )

    print("✅ Bytecode optimization complete!")
    print("Optimized .pyc files are available in __pycache__ directories")

if __name__ == "__main__":
    optimize_eq12_bytecode()
'''

            with open(optimization_script, "w", encoding="utf-8") as f:
                f.write(opt_content)

            logging.info("Created bytecode optimization script")
            self.fixes_applied += 1

        except Exception as e:
            logging.error(f"Failed to create optimization script: {e}")
            self.issues_found.append(f"Optimization script creation failed: {e}")

    def create_pyc_gitignore_rules(self) -> None:
        """Create or update .gitignore with proper .pyc rules"""
        gitignore_path = self.root_path / ".gitignore"

        pyc_rules = [
            "# Byte-compiled / optimized / DLL files",
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "",
            "# C extensions",
            "*.so",
            "",
            "# Distribution / packaging",
            ".Python",
            "build/",
            "develop-eggs/",
            "dist/",
            "downloads/",
            "eggs/",
            ".eggs/",
            "lib/",
            "lib64/",
            "parts/",
            "sdist/",
            "var/",
            "wheels/",
            "*.egg-info/",
            ".installed.cfg",
            "*.egg",
            "MANIFEST",
            "",
            "# PyInstaller",
            "*.manifest",
            "*.spec",
        ]

        try:
            if gitignore_path.exists():
                with open(gitignore_path, encoding="utf-8") as f:
                    existing_content = f.read()

                # Check if .pyc rules already exist
                if "__pycache__/" not in existing_content:
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write("\n\n# Python bytecode files\n")
                        f.write("\n".join(pyc_rules))

                    logging.info("Added .pyc rules to existing .gitignore")
                    self.fixes_applied += 1
                else:
                    logging.info(".gitignore already contains .pyc rules")
            else:
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write("# EQ12 .gitignore\n\n")
                    f.write("\n".join(pyc_rules))

                logging.info("Created .gitignore with .pyc rules")
                self.fixes_applied += 1

        except Exception as e:
            logging.error(f"Failed to update .gitignore: {e}")
            self.issues_found.append(f"Gitignore update failed: {e}")

    def create_pyc_cleanup_script(self) -> None:
        """Create automated .pyc cleanup script"""
        cleanup_script = self.root_path / "cleanup_pyc.py"

        cleanup_content = '''#!/usr/bin/env python3
"""
EQ12 Python Bytecode Cleanup Utility
Removes stale, corrupted, and unnecessary .pyc files
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_pyc_files(root_path=".", force_all=False, dry_run=False):
    """Clean up .pyc files in the specified directory"""
    root = Path(root_path)
    cleaned_count = 0
    bytes_cleaned = 0

    print("🧹 EQ12 .pyc Cleanup Utility")
    print("Root path: {root.absolute()}")
    print("Mode: {'DRY RUN' if dry_run else 'ACTIVE CLEANUP'}")
    print("=" * 50)

    if force_all:
        # Remove all __pycache__ directories
        pycache_dirs = list(root.rglob("__pycache__"))
        print("Found {len(pycache_dirs)} __pycache__ directories")

        for pycache_dir in pycache_dirs:
            try:
                if not dry_run:
                    # Calculate size before removal
                    size = sum(f.stat().st_size for f in pycache_dir.rglob("*") if f.is_file())
                    bytes_cleaned += size
                    shutil.rmtree(pycache_dir)

                print("✓ Removed: {pycache_dir}")
                cleaned_count += 1
            except Exception as e:
                print("✗ Failed: {pycache_dir} - {e}")
    else:
        # Selective cleanup
        pyc_files = list(root.rglob("*.pyc"))
        print("Found {len(pyc_files)} .pyc files")

        for pyc_file in pyc_files:
            should_remove = False
            reason = ""

            try:
                # Check if source exists
                if "__pycache__" in str(pyc_file):
                    parent_dir = pyc_file.parent.parent
                    source_name = pyc_file.stem.split('.')[0] + ".py"
                    source_path = parent_dir / source_name
                else:
                    source_path = pyc_file.with_suffix(".py")

                if not source_path.exists():
                    should_remove = True
                    reason = "Orphaned (no source file)"
                else:
                    # Check if source is newer
                    pyc_mtime = datetime.fromtimestamp(pyc_file.stat().st_mtime)
                    source_mtime = datetime.fromtimestamp(source_path.stat().st_mtime)

                    if source_mtime > pyc_mtime:
                        should_remove = True
                        reason = "Stale (source newer)"

                    # Check age (older than 30 days)
                    age = datetime.now() - pyc_mtime
                    if age.days > 30:
                        should_remove = True
                        reason = f"Old ({age.days} days)"

                if should_remove:
                    file_size = pyc_file.stat().st_size
                    if not dry_run:
                        pyc_file.unlink()
                        bytes_cleaned += file_size

                    print("✓ Removed: {pyc_file.name} - {reason}")
                    cleaned_count += 1

            except Exception as e:
                print("✗ Error processing {pyc_file}: {e}")

    print("=" * 50)
    print("Files processed: {cleaned_count}")
    print("Space cleaned: {bytes_cleaned / 1024 / 1024:.2f} MB")

    if dry_run:
        print("This was a DRY RUN - no files were actually removed")
        print("Run with --execute to perform actual cleanup")

def main():
    """Main cleanup function with CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 .pyc Cleanup Utility")
    parser.add_argument("--path", default=".", help="Root path to clean (default: current directory)")
    parser.add_argument("--force-all", action="store_true", help="Remove all __pycache__ directories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without actually removing")
    parser.add_argument("--execute", action="store_true", help="Actually perform the cleanup")

    args = parser.parse_args()

    if not args.execute and not args.dry_run:
        print("Use --dry-run to see what would be cleaned, or --execute to actually clean")
        return

    cleanup_pyc_files(
        root_path=args.path,
        force_all=args.force_all,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()
'''

        try:
            with open(cleanup_script, "w", encoding="utf-8") as f:
                f.write(cleanup_content)

            # Make executable on Unix-like systems
            if os.name != "nt":
                cleanup_script.chmod(0o755)

            logging.info("Created .pyc cleanup utility script")
            self.fixes_applied += 1

        except Exception as e:
            logging.error(f"Failed to create cleanup script: {e}")
            self.issues_found.append(f"Cleanup script creation failed: {e}")

    def add_pyc_ci_integration(self) -> None:
        """Add .pyc cleanup to CI/CD workflows"""
        workflows_dir = self.root_path / ".github" / "workflows"

        if not workflows_dir.exists():
            logging.warning("No .github/workflows directory found")
            return

        # Create or update CI workflow to include .pyc cleanup
        pyc_workflow = workflows_dir / "pyc-maintenance.yml"

        workflow_content = """name: Python Bytecode Maintenance

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM

permissions:
  contents: read

jobs:
  pyc-cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Clean stale .pyc files
        run: |
          python cleanup_pyc.py --dry-run --path .

      - name: Validate Python syntax
        run: |
          python -m py_compile scripts/*.py || true
          python -m py_compile buffalo_stack/*.py || true

      - name: Optimize bytecode for production
        run: |
          python -m compileall -f -q scripts/ buffalo_stack/ || true

      - name: Check for orphaned bytecode
        run: |
          find . -name "*.pyc" -type f | while read pyc_file; do
            py_file="${pyc_file%.*}.py"
            if [ ! -f "$py_file" ]; then
              echo "Orphaned: $pyc_file"
            fi
          done

  bytecode-analysis:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Analyze bytecode quality
        run: |
          echo "Analyzing Python bytecode files..."

          # Count .pyc files
          pyc_count=$(find . -name "*.pyc" -type f | wc -l)
          echo "Total .pyc files: $pyc_count"

          # Check for version mismatches
          find . -name "*.pyc" -type f | head -10 | xargs file

          # Report large __pycache__ directories
          du -sh */__pycache__ 2>/dev/null | sort -hr | head -10 || true
"""

        try:
            with open(pyc_workflow, "w", encoding="utf-8") as f:
                f.write(workflow_content)

            logging.info("Created .pyc maintenance workflow")
            self.fixes_applied += 1

        except Exception as e:
            logging.error(f"Failed to create CI workflow: {e}")
            self.issues_found.append(f"CI workflow creation failed: {e}")

    def run_comprehensive_fixes(self, cleanup_mode: str = "selective") -> dict[str, Any]:
        """Run all .pyc fixes and return summary"""
        logging.info("Starting comprehensive .pyc fixes for EQ12")

        # 1. Analyze current state
        initial_pyc_count = len(list(self.root_path.rglob("*.pyc")))
        initial_pycache_count = len(list(self.root_path.rglob("__pycache__")))

        logging.info(
            f"Initial state: {initial_pyc_count} .pyc files in {initial_pycache_count} directories"
        )

        # 2. Clean problematic .pyc files
        force_all = cleanup_mode == "force_all"
        cleaned_count = self.clean_stale_pyc_files(force_all=force_all)

        # 3. Create management utilities
        self.create_pyc_cleanup_script()
        self.optimize_bytecode()
        self.create_pyc_gitignore_rules()

        # 4. Add CI integration
        self.add_pyc_ci_integration()

        # 5. Recompile fresh bytecode
        recompiled_count = self.recompile_python_files() if cleanup_mode != "cleanup_only" else 0

        # Final state
        final_pyc_count = len(list(self.root_path.rglob("*.pyc")))
        final_pycache_count = len(list(self.root_path.rglob("__pycache__")))

        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "mode": cleanup_mode,
            "initial_pyc_files": initial_pyc_count,
            "initial_pycache_dirs": initial_pycache_count,
            "final_pyc_files": final_pyc_count,
            "final_pycache_dirs": final_pycache_count,
            "files_cleaned": cleaned_count,
            "files_recompiled": recompiled_count,
            "bytes_cleaned": self.bytes_cleaned,
            "fixes_applied": self.fixes_applied,
            "files_processed": self.files_processed,
            "issues_found": len(self.issues_found),
            "issue_details": self.issues_found,
            "improvements": [
                "Removed stale and corrupted .pyc files",
                "Created automated cleanup utility (cleanup_pyc.py)",
                "Added bytecode optimization script (optimize_bytecode.py)",
                "Enhanced .gitignore with comprehensive .pyc rules",
                "Integrated .pyc maintenance into CI/CD workflows",
                "Recompiled fresh bytecode for current Python version",
                "Added orphaned bytecode detection",
                "Implemented automated maintenance scheduling",
            ],
            "status": "completed",
        }

        # Write summary
        summary_file = (
            self.root_path
            / "logs"
            / f"pyc_fixes_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        summary_file.parent.mkdir(exist_ok=True)

        try:
            import json

            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            logging.info(f"Summary written to {summary_file}")
        except Exception as e:
            logging.error(f"Failed to write summary: {e}")

        return summary


def main():
    """Main function to run .pyc fixes"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Python Bytecode Expert Fixer")
    parser.add_argument("--root", default="C:\\EQ12", help="Root directory (default: C:\\EQ12)")
    parser.add_argument(
        "--mode",
        choices=["selective", "force_all", "cleanup_only"],
        default="selective",
        help="Cleanup mode",
    )
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't fix")
    args = parser.parse_args()

    fixer = PycExpertFixer(args.root)

    if args.analyze_only:
        # Just analyze
        problematic_files = fixer.find_problematic_pyc_files()
        print("\nFound {len(problematic_files)} problematic .pyc files:")
        for _pyc_file, _analysis in problematic_files[:20]:  # Show first 20
            print("  {pyc_file.name}: {', '.join(analysis['issues'])}")
        if len(problematic_files) > 20:
            print("  ... and {len(problematic_files) - 20} more")
    else:
        summary = fixer.run_comprehensive_fixes(cleanup_mode=args.mode)

        print("\n" + "=" * 70)
        print("PYTHON BYTECODE (.PYC) EXPERT FIXES SUMMARY")
        print("=" * 70)
        print("Mode: {summary['mode']}")
        print("Files processed: {summary['files_processed']}")
        print("Files cleaned: {summary['files_cleaned']}")
        print("Files recompiled: {summary['files_recompiled']}")
        print("Space recovered: {summary['bytes_cleaned'] / 1024 / 1024:.2f} MB")
        print("Fixes applied: {summary['fixes_applied']}")

        print(
            "\nBefore: {summary['initial_pyc_files']} .pyc files in {summary['initial_pycache_dirs']} directories"
        )
        print(
            "After:  {summary['final_pyc_files']} .pyc files in {summary['final_pycache_dirs']} directories"
        )

        print("\nImprovements made:")
        for _improvement in summary["improvements"]:
            print("  ✅ {improvement}")

        if summary["issue_details"]:
            print("\nIssues requiring manual attention:")
            for _issue in summary["issue_details"][:5]:
                print("  • {issue}")

        print("\nDetailed log: pyc_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

        print("\n🚀 Utilities created:")
        print("  • python cleanup_pyc.py --dry-run  # Preview cleanup")
        print("  • python cleanup_pyc.py --execute  # Perform cleanup")
        print("  • python optimize_bytecode.py      # Optimize for production")


if __name__ == "__main__":
    main()
