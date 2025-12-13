# -*- coding: utf-8 -*-
"""
EQ12 Workspace Guard - Auto-Scanning UTF-8 Protection System
Permanent immunity against encoding corruption, invalid JSON, broken scripts
Buffalo NY 14215 Content Empire Protection
"""

import os
import json
import re
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Force UTF-8 for all operations
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class EQ12WorkspaceGuard:
    def __init__(self):
        self.root_path = Path("C:/EQ12")
        self.safe_extensions = (".txt", ".md", ".json", ".py", ".ps1", ".yaml", ".yml", ".html", ".css", ".js", ".ts")
        self.excluded_dirs = {"node_modules", ".git", "__pycache__", ".vscode", "venv", ".env"}

        # Setup logging
        self.log_path = self.root_path / "logs" / f"workspace_guard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.log_path.parent.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        self.logger = logging.getLogger(__name__)

    def safe_read_file(self, file_path: Path) -> Tuple[str, bool]:
        """Safely read file with UTF-8 fallback"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, True
        except UnicodeDecodeError:
            try:
                with open(file_path, 'rb') as f:
                    raw_bytes = f.read()
                content = raw_bytes.decode('utf-8', errors='replace')
                return content, False
            except Exception as e:
                self.logger.error(f"Cannot read {file_path}: {e}")
                return "", False

    def safe_write_file(self, file_path: Path, content: str) -> bool:
        """Safely write file with UTF-8 encoding"""
        try:
            with open(file_path, 'w', encoding='utf-8', newline='\\n') as f:
                f.write(content)
            return True
        except Exception as e:
            self.logger.error(f"Cannot write {file_path}: {e}")
            return False

    def clean_utf8_file(self, file_path: Path) -> Dict:
        """Clean and ensure file is proper UTF-8"""
        result = {
            "file": str(file_path),
            "status": "skipped",
            "issues_found": [],
            "issues_fixed": []
        }

        if not file_path.exists() or file_path.suffix not in self.safe_extensions:
            return result

        # Read file with encoding detection
        content, was_utf8 = self.safe_read_file(file_path)
        if not content:
            result["status"] = "error"
            result["issues_found"].append("unreadable_file")
            return result

        original_content = content
        issues_found = []
        issues_fixed = []

        # Check if file was not UTF-8
        if not was_utf8:
            issues_found.append("non_utf8_encoding")

        # Remove BOM if present
        if content.startswith('\\ufeff'):
            content = content[1:]
            issues_found.append("bom_present")
            issues_fixed.append("bom_removed")

        # Replace problematic characters
        problematic_chars = {\n            '\\r\\n': '\\n',  # Windows line endings\n            '\\r': '\\n',    # Mac line endings\n            '\\u0000': '',   # Null bytes\n            '\\ufeff': '',   # BOM markers\n            '\\u200b': '',   # Zero-width space\n            '\\u200c': '',   # Zero-width non-joiner\n            '\\u200d': '',   # Zero-width joiner\n        }\n        \n        for bad_char, replacement in problematic_chars.items():\n            if bad_char in content:\n                content = content.replace(bad_char, replacement)\n                issues_found.append(f"problematic_char_{bad_char.encode('unicode_escape').decode('ascii')}")\n                issues_fixed.append(f"fixed_char_{bad_char.encode('unicode_escape').decode('ascii')}")\n        \n        # Ensure file ends with single newline\n        content = content.rstrip() + '\\n'\n        \n        # Special handling for JSON files\n        if file_path.suffix == '.json':\n            try:\n                json_data = json.loads(content)\n                # Re-serialize with proper UTF-8 formatting\n                content = json.dumps(json_data, ensure_ascii=False, indent=2) + '\\n'\n                issues_fixed.append("json_reformatted")\n            except json.JSONDecodeError as e:\n                issues_found.append(f"invalid_json_{str(e)}")\n                result["status"] = "json_error"\n        \n        # Write back if changes were made\n        if content != original_content or not was_utf8:\n            if self.safe_write_file(file_path, content):\n                result["status"] = "fixed" if issues_found else "verified"\n                issues_fixed.append("utf8_encoding_enforced")\n            else:\n                result["status"] = "write_error"\n        else:\n            result["status"] = "clean"\n        \n        result["issues_found"] = issues_found\n        result["issues_fixed"] = issues_fixed\n        return result

    def validate_json_files(self) -> List[Dict]:\n        """Validate all JSON files in workspace"""\n        invalid_json = []\n        \n        for json_file in self.root_path.rglob('*.json'):\n            if any(excluded in json_file.parts for excluded in self.excluded_dirs):\n                continue\n            \n            try:\n                with open(json_file, 'r', encoding='utf-8') as f:\n                    json.load(f)\n            except json.JSONDecodeError as e:\n                invalid_json.append({\n                    "file": str(json_file),\n                    "error": str(e),\n                    "line": getattr(e, 'lineno', 'unknown'),\n                    "column": getattr(e, 'colno', 'unknown')\n                })\n            except Exception as e:\n                invalid_json.append({\n                    "file": str(json_file),\n                    "error": f"Read error: {e}",\n                    "line": "unknown",\n                    "column": "unknown"\n                })\n        \n        return invalid_json\n    \n    def scan_workspace(self) -> Dict:\n        """Scan entire workspace and fix UTF-8 issues"""\n        print(" EQ12 Workspace Guard - Starting scan...")\n        \n        results = {\n            "timestamp": datetime.now().isoformat(),\n            "workspace": str(self.root_path),\n            "files_scanned": 0,\n            "files_fixed": 0,\n            "files_clean": 0,\n            "files_errors": 0,\n            "total_issues_found": 0,\n            "total_issues_fixed": 0,\n            "file_results": []\n        }\n        \n        # Scan all files\n        for file_path in self.root_path.rglob('*'):\n            if file_path.is_file() and file_path.suffix in self.safe_extensions:\n                # Skip excluded directories\n                if any(excluded in file_path.parts for excluded in self.excluded_dirs):\n                    continue\n                \n                file_result = self.clean_utf8_file(file_path)\n                results["file_results"].append(file_result)\n                results["files_scanned"] += 1\n                \n                if file_result["status"] == "fixed":\n                    results["files_fixed"] += 1\n                elif file_result["status"] == "clean":\n                    results["files_clean"] += 1\n                elif "error" in file_result["status"]:\n                    results["files_errors"] += 1\n                \n                results["total_issues_found"] += len(file_result["issues_found"])\n                results["total_issues_fixed"] += len(file_result["issues_fixed"])\n                \n                # Progress indicator\n                if results["files_scanned"] % 100 == 0:\n                    print(f" Processed {results['files_scanned']} files...")\n        \n        # Save results\n        with open(self.log_path, 'w', encoding='utf-8') as f:\n            json.dump(results, f, ensure_ascii=False, indent=2)\n        \n        # Print summary\n        print(f"\\n EQ12 Workspace Guard Complete!")\n        print(f" Files scanned: {results['files_scanned']}")\n        print(f" Files fixed: {results['files_fixed']}")\n        print(f" Files clean: {results['files_clean']}")\n        print(f" Files with errors: {results['files_errors']}")\n        print(f" Total issues found: {results['total_issues_found']}")\n        print(f" Total issues fixed: {results['total_issues_fixed']}")\n        print(f" Log saved: {self.log_path}")\n        \n        return results\n    \n    def quick_health_check(self) -> Dict:\n        """Quick health check of critical files"""    \n        critical_files = [\n            self.root_path / "scripts" / "revenue_tracker_hardened.py",\n            self.root_path / "logs" / "revenue_tracking.json",\n            Path(os.environ.get('APPDATA', '')) / "Code" / "User" / "settings.json"\n        ]\n        \n        health_status = {\n            "timestamp": datetime.now().isoformat(),\n            "critical_files_status": [],\n            "overall_health": "healthy"\n        }\n        \n        for file_path in critical_files:\n            if file_path.exists():\n                file_result = self.clean_utf8_file(file_path)\n                status = {\n                    "file": str(file_path),\n                    "exists": True,\n                    "utf8_compliant": file_result["status"] in ["clean", "fixed"],\n                    "issues": file_result["issues_found"]\n                }\n                \n                if file_result["status"] in ["error", "write_error", "json_error"]:\n                    health_status["overall_health"] = "unhealthy"\n                    \n            else:\n                status = {\n                    "file": str(file_path),\n                    "exists": False,\n                    "utf8_compliant": False,\n                    "issues": ["file_missing"]\n                }\n                health_status["overall_health"] = "warning"\n            \n            health_status["critical_files_status"].append(status)\n        \n        return health_status\n\ndef main():\n    \"\"\"Main entry point for EQ12 Workspace Guard\"\"\"\n    import sys\n    \n    guard = EQ12WorkspaceGuard()\n    \n    if len(sys.argv) > 1 and sys.argv[1] == \"--quick\":\n        health = guard.quick_health_check()\n        print(f" Health Status: {health['overall_health'].upper()}\")\n    elif len(sys.argv) > 1 and sys.argv[1] == \"--json-check\":\n        invalid = guard.validate_json_files()\n        if invalid:\n            print(f\" {len(invalid)} JSON validation errors found\")\n            for error in invalid[:5]:  # Show first 5 errors\n                print(f\"  {error['file']}: {error['error']}\")\n        else:\n            print(\" All JSON files valid\")\n    else:\n        # Full workspace scan\n        results = guard.scan_workspace()\n        return results\n\nif __name__ == \"__main__\":\n    # EQ12 Immunity System Active\n    print(\" EQ12 UTF-8 Immunity System - Buffalo NY 14215\")\n    main()\n
