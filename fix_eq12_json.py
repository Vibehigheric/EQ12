#!/usr/bin/env python3
"""
EQ12 JSON Expert Fixer
Comprehensive JSON validation, error handling, and standardization across the EQ12 codebase.
"""

import json
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"json_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(),
    ],
)


class EQ12JsonFixer:
    def __init__(self, root_path: str = "C:\\EQ12"):
        self.root_path = Path(root_path)
        self.fixes_applied = 0
        self.files_processed = 0
        self.errors_found = []

    def validate_json_file(self, file_path: Path) -> dict[str, Any]:
        """Validate a JSON file and return validation results"""
        result = {"valid": False, "error": None, "content": None, "suggestions": []}

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for common JSON issues
            if not content.strip():
                result["error"] = "Empty file"
                result["suggestions"].append("Add valid JSON content")
                return result

            # Try to parse JSON
            parsed = json.loads(content)
            result["valid"] = True
            result["content"] = parsed

            # Additional validations
            if isinstance(parsed, dict):
                # Check for common config file requirements
                if file_path.name == "config.json":
                    result["suggestions"].extend(self._validate_config_json(parsed, file_path))

        except json.JSONDecodeError as e:
            result["error"] = f"JSON decode error: {e}"
            result["suggestions"].append("Fix JSON syntax errors")

        except UnicodeDecodeError as e:
            result["error"] = f"Encoding error: {e}"
            result["suggestions"].append("Check file encoding (should be UTF-8)")

        except Exception as e:
            result["error"] = f"Unexpected error: {e}"

        return result

    def _validate_config_json(self, content: dict[str, Any], file_path: Path) -> list[str]:
        """Validate config.json files for required fields"""
        suggestions = []

        if "JobSearchBot" in str(file_path):
            required_fields = ["keywords", "locations", "min_hourly", "recipient"]
            for field in required_fields:
                if field not in content:
                    suggestions.append(f"Missing required field: {field}")

        elif "EdgeGodUnified" in str(file_path):
            required_fields = ["email_recipient", "telegram_enabled"]
            for field in required_fields:
                if field not in content:
                    suggestions.append(f"Missing required field: {field}")

        return suggestions

    def fix_python_json_handling(self, file_path: Path) -> bool:
        """Fix JSON handling in Python files"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            fixes_made = 0

            # Pattern 1: json.load without error handling
            pattern1 = r"(\s*)(.*?)\s*=\s*json\.load\(([^)]+)\)"

            def replace_json_load(match):
                indent = match.group(1)
                var_assignment = match.group(2).strip()
                file_arg = match.group(3)
                return f"""{indent}try:
{indent}    {var_assignment} = json.load({file_arg})
{indent}except json.JSONDecodeError as e:
{indent}    logging.error(f"Failed to parse JSON from {{file_path}}: {{e}}")
{indent}    raise
{indent}except FileNotFoundError as e:
{indent}    logging.error(f"JSON file not found: {{e}}")
{indent}    raise"""

            # Only apply if not already wrapped in try-except
            if "json.load(" in content and "except json.JSONDecodeError" not in content:
                new_content = re.sub(pattern1, replace_json_load, content)
                if new_content != content:
                    content = new_content
                    fixes_made += 1

            # Pattern 2: json.dump without error handling
            pattern2 = r"(\s*)json\.dump\(([^)]+)\)"

            def replace_json_dump(match):
                indent = match.group(1)
                args = match.group(2)
                return f"""{indent}try:
{indent}    json.dump({args})
{indent}except (IOError, OSError) as e:
{indent}    logging.error(f"Failed to write JSON: {{e}}")
{indent}    raise"""

            if "json.dump(" in content and "except (IOError, OSError)" not in content:
                new_content = re.sub(pattern2, replace_json_dump, content)
                if new_content != content:
                    content = new_content
                    fixes_made += 1

            # Pattern 3: Add json import if missing but json functions are used
            if (
                "json.load(" in content or "json.dump(" in content or "json.loads(" in content
            ) and "import json" not in content:
                # Find the best place to add import
                lines = content.split("\n")
                import_line = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith("import ") or line.strip().startswith("from "):
                        import_line = i + 1

                lines.insert(import_line, "import json")
                content = "\n".join(lines)
                fixes_made += 1

            # Pattern 4: Improve json.loads error handling
            pattern4 = r"(\s*)(.*?)\s*=\s*json\.loads\(([^)]+)\)"

            def replace_json_loads(match):
                indent = match.group(1)
                var_assignment = match.group(2).strip()
                str_arg = match.group(3)
                return f"""{indent}try:
{indent}    {var_assignment} = json.loads({str_arg})
{indent}except json.JSONDecodeError as e:
{indent}    logging.error(f"Failed to parse JSON string: {{e}}")
{indent}    {var_assignment} = {{}}  # Safe fallback"""

            if "json.loads(" in content and "except json.JSONDecodeError" not in content:
                new_content = re.sub(pattern4, replace_json_loads, content)
                if new_content != content:
                    content = new_content
                    fixes_made += 1

            if fixes_made > 0 and content != original_content:
                # Backup original file
                backup_path = file_path.with_suffix(
                    f"{file_path.suffix}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                shutil.copy2(file_path, backup_path)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                logging.info(f"Applied {fixes_made} JSON fixes to {file_path}")
                self.fixes_applied += fixes_made
                return True

        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            self.errors_found.append(f"{file_path}: {e}")

        return False

    def create_json_validation_utilities(self) -> None:
        """Add JSON validation utilities to eq12_config.py"""
        config_file = self.root_path / "eq12_config.py"

        if not config_file.exists():
            logging.warning("eq12_config.py not found, skipping JSON utilities addition")
            return

        try:
            with open(config_file, encoding="utf-8") as f:
                content = f.read()

            # Check if JSON utilities already exist
            if "def validate_json_file" in content:
                logging.info("JSON validation utilities already exist in eq12_config.py")
                return

            # JSON validation utilities to add
            json_utils = '''

# JSON Validation Utilities
def validate_json_file(file_path: Union[str, Path], schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Validate a JSON file and optionally check against a schema.

    Args:
        file_path: Path to JSON file
        schema: Optional schema dictionary for validation

    Returns:
        Dictionary with validation results: {"valid": bool, "error": str, "content": Any}
    """
    result = {"valid": False, "error": None, "content": None}

    try:
        file_path = Path(file_path)
        if not file_path.exists():
            result["error"] = f"File not found: {file_path}"
            return result

        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        result["valid"] = True
        result["content"] = content

        # Basic schema validation if provided
        if schema and isinstance(schema, dict):
            if isinstance(content, dict):
                for required_key in schema.get("required", []):
                    if required_key not in content:
                        result["error"] = f"Missing required key: {required_key}"
                        result["valid"] = False
                        break

    except json.JSONDecodeError as e:
        result["error"] = f"JSON decode error: {e}"
    except Exception as e:
        result["error"] = f"Validation error: {e}"

    return result


def load_json_with_fallback(file_path: Union[str, Path], fallback: Any = None) -> Any:
    """Load JSON with safe fallback handling.

    Args:
        file_path: Path to JSON file
        fallback: Value to return if loading fails

    Returns:
        JSON content or fallback value
    """
    try:
        file_path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Failed to load JSON from {file_path}: {e}")
        return fallback


def write_json_safely(file_path: Union[str, Path], data: Any, backup: bool = True) -> bool:
    """Write JSON with safe backup and error handling.

    Args:
        file_path: Path to write JSON file
        data: Data to write
        backup: Whether to create backup of existing file

    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)

        # Create backup if file exists and backup is requested
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(f'{file_path.suffix}.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            shutil.copy2(file_path, backup_path)

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON with proper formatting
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        logging.error(f"Failed to write JSON to {file_path}: {e}")
        return False


def get_config_schema(config_type: str) -> Dict[str, Any]:
    """Get JSON schema for different config types.

    Args:
        config_type: Type of config ('job_search', 'edgegod_unified', etc.)

    Returns:
        Schema dictionary
    """
    schemas = {
        "job_search": {
            "required": ["keywords", "locations", "min_hourly", "recipient"],
            "optional": ["adzuna_app_id", "adzuna_app_key", "telegram_enabled"]
        },
        "edgegod_unified": {
            "required": ["email_recipient", "telegram_enabled"],
            "optional": ["min_ev_percent", "simulations", "caps"]
        },
        "watchlist": {
            "required": [],
            "optional": ["name", "url", "target_price", "store", "type", "min_discount"]
        }
    }

    return schemas.get(config_type, {"required": [], "optional": []})
'''

            # Add the utilities before the final if __name__ == '__main__' block
            if "if __name__ == '__main__':" in content:
                content = content.replace(
                    "if __name__ == '__main__':",
                    json_utils + "\n\nif __name__ == '__main__':",
                )
            else:
                content += json_utils

            # Backup and write
            backup_path = config_file.with_suffix(
                f"{config_file.suffix}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(config_file, backup_path)

            with open(config_file, "w", encoding="utf-8") as f:
                f.write(content)

            logging.info("Added JSON validation utilities to eq12_config.py")
            self.fixes_applied += 1

        except Exception as e:
            logging.error(f"Error adding JSON utilities to eq12_config.py: {e}")
            self.errors_found.append(f"eq12_config.py utilities: {e}")

    def fix_json_files(self) -> None:
        """Fix and validate all JSON files in the project"""
        json_files = list(self.root_path.rglob("*.json"))

        # Filter out build artifacts and temp files
        json_files = [
            f
            for f in json_files
            if not any(
                skip in str(f)
                for skip in [
                    "node_modules",
                    ".git",
                    "obj",
                    "bin",
                    "__pycache__",
                    ".vscode",
                ]
            )
        ]

        logging.info(f"Found {len(json_files)} JSON files to validate")

        for json_file in json_files:
            self.files_processed += 1
            logging.info(f"Validating {json_file}")

            result = self.validate_json_file(json_file)

            if not result["valid"]:
                logging.warning(f"JSON validation failed for {json_file}: {result['error']}")
                self.errors_found.append(f"{json_file}: {result['error']}")
            else:
                logging.info(f"✓ {json_file} is valid JSON")

            if result["suggestions"]:
                for suggestion in result["suggestions"]:
                    logging.info(f"  Suggestion: {suggestion}")

    def fix_python_files(self) -> None:
        """Fix JSON handling in all Python files"""
        python_files = list(self.root_path.rglob("*.py"))

        # Filter out build artifacts and temp files
        python_files = [
            f
            for f in python_files
            if not any(
                skip in str(f) for skip in ["__pycache__", ".git", "venv", "env", ".pytest_cache"]
            )
        ]

        logging.info(f"Found {len(python_files)} Python files to check for JSON handling")

        for py_file in python_files:
            if self.fix_python_json_handling(py_file):
                logging.info(f"✓ Applied JSON fixes to {py_file}")

    def run_comprehensive_fixes(self) -> dict[str, Any]:
        """Run all JSON fixes and return summary"""
        logging.info("Starting comprehensive JSON fixes for EQ12 codebase")

        # 1. Validate and fix JSON files
        self.fix_json_files()

        # 2. Fix Python JSON handling
        self.fix_python_files()

        # 3. Add JSON utilities to eq12_config.py
        self.create_json_validation_utilities()

        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": self.files_processed,
            "fixes_applied": self.fixes_applied,
            "errors_found": len(self.errors_found),
            "error_details": self.errors_found,
            "status": "completed",
        }

        # Write summary to logs
        summary_file = (
            self.root_path
            / "logs"
            / f"json_fixes_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        summary_file.parent.mkdir(exist_ok=True)

        try:
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            logging.info(f"Summary written to {summary_file}")
        except Exception as e:
            logging.error(f"Failed to write summary: {e}")

        return summary


def main():
    """Main function to run JSON fixes"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 JSON Expert Fixer")
    parser.add_argument("--root", default="C:\\EQ12", help="Root directory (default: C:\\EQ12)")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't fix")
    args = parser.parse_args()

    fixer = EQ12JsonFixer(args.root)

    if args.validate_only:
        fixer.fix_json_files()  # Just validates
    else:
        summary = fixer.run_comprehensive_fixes()

        print("\n" + "=" * 50)
        print("JSON FIXES SUMMARY")
        print("=" * 50)
        print(f"Files processed: {summary['files_processed']}")
        print(f"Fixes applied: {summary['fixes_applied']}")
        print(f"Errors found: {summary['errors_found']}")

        if summary["error_details"]:
            print("\nErrors requiring manual attention:")
            for error in summary["error_details"][:10]:  # Show first 10
                print(f"  • {error}")

        print(f"\nDetailed log: json_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


if __name__ == "__main__":
    main()
