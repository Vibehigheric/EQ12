#!/usr/bin/env python3
"""
EQ12 ChatGPT Codemod System
Large-scale code transformations with proper cost guards.
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# Import EQ12 modules
try:
    from eq12_free_guard import get_cost_guards, is_free_mode
    from eq12_responses_client import EQ12ResponsesClient
except ImportError as e:
    print(f"ERROR: Could not import EQ12 modules: {e}")
    print("Make sure you're running from the EQ12 root directory with .venv activated")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/codemod.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12CodemodSystem:
    """ChatGPT-powered codemod system for EQ12."""

    def __init__(self):
        self.client = None
        self.patches_dir = Path("logs/patches")
        self.patches_dir.mkdir(exist_ok=True)

        # Initialize AI client if not in free mode
        if not is_free_mode():
            try:
                self.client = EQ12ResponsesClient()
                logger.info("ChatGPT client initialized for codemods")
            except Exception as e:
                logger.warning(f"Could not initialize ChatGPT client: {e}")
        else:
            logger.info("Free mode: Using mock transformations")

    def get_file_patterns(self, plan_type: str) -> list[str]:
        """Get file patterns for different codemod plans."""
        patterns = {
            "utc_fixes": ["**/*.py"],
            "parlay_sanitizer": ["**/parlay*.py", "**/eq12_*optimizer*.py"],
            "cost_guard_insertion": ["**/*.py"],
            "ruff_modernize": [".vscode/settings.json", "pyproject.toml"],
            "logging_hardening": ["**/*.py"],
        }
        return patterns.get(plan_type, ["**/*.py"])

    def collect_target_files(self, patterns: list[str]) -> list[Path]:
        """Collect files matching the given patterns."""
        files = []
        exclude_patterns = [
            ".venv",
            "node_modules",
            "__pycache__",
            ".git",
            "logs",
            "data/github_repos",
        ]

        for pattern in patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file() and not any(
                    exc in str(file_path) for exc in exclude_patterns
                ):
                    files.append(file_path)

        return sorted(set(files))

    def create_codemod_prompt(self, plan_type: str, files: list[Path]) -> str:
        """Create a ChatGPT prompt for the codemod."""

        file_contents = {}
        for file_path in files[:10]:  # Limit to first 10 files for token management
            try:
                with open(file_path, encoding="utf-8") as f:
                    file_contents[str(file_path)] = f.read()
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")

        prompts = {
            "utc_fixes": """
Fix timezone issues in the following EQ12 Python files. Make all datetime operations timezone-aware using UTC.

REQUIREMENTS:
- Replace datetime.utcnow() with datetime.now(timezone.utc)
- Convert naive datetime comparisons to timezone-aware
- Use datetime.fromisoformat().astimezone(timezone.utc) for ISO string parsing
- Add timezone imports where needed
- Preserve existing functionality

FILES TO TRANSFORM:
{json.dumps(file_contents, indent=2)}

Return a JSON response with file paths as keys and transformed content as values.
""",
            "parlay_sanitizer": """
Add parlay sanitization and deduplication to EQ12 betting optimizers.

REQUIREMENTS:
- Deduplicate moneyline legs across books in the same parlay
- Prevent correlated legs from same game
- Add sanitizer helper imports
- Add validation before parlay creation
- Preserve existing EV calculations

FILES TO TRANSFORM:
{json.dumps(file_contents, indent=2)}

Return a JSON response with file paths as keys and transformed content as values.
""",
            "cost_guard_insertion": """
Add EQ12 cost guards before all OpenAI API calls.

REQUIREMENTS:
- Import eq12_free_guard functions
- Check is_free_mode() before API calls
- Add get_cost_guards().check_request_allowed() validation
- Raise appropriate errors when blocked
- Log all cost guard decisions

FILES TO TRANSFORM:
{json.dumps(file_contents, indent=2)}

Return a JSON response with file paths as keys and transformed content as values.
""",
        }

        return prompts.get(plan_type, "Generic codemod transformation")

    def execute_codemod(self, plan_type: str, dry_run: bool = True) -> bool:
        """Execute a codemod plan."""
        logger.info(f"Starting codemod plan: {plan_type}")

        # Collect target files
        patterns = self.get_file_patterns(plan_type)
        files = self.collect_target_files(patterns)

        if not files:
            logger.warning(f"No files found for patterns: {patterns}")
            return False

        logger.info(f"Found {len(files)} files to process")

        # Check if we have AI client
        if not self.client and not is_free_mode():
            logger.error("No AI client available and not in free mode")
            return False

        # Create prompt
        prompt = self.create_codemod_prompt(plan_type, files)

        # Generate transformations
        if is_free_mode():
            # Mock transformation for free mode
            transformations = self._mock_transformations(plan_type, files)
            logger.info("Generated mock transformations (free mode)")
        else:
            # Real AI transformation
            try:
                guards = get_cost_guards()
                allowed, reason = guards.check_request_allowed(
                    "codemod", 0.10)  # Estimate $0.10
                if not allowed:
                    logger.error(f"Cost guard blocked codemod: {reason}")
                    return False

                response = self.client.create_conversation().send_message(prompt)
                transformations = self._parse_ai_response(response)
                logger.info("Generated AI transformations")
            except Exception as e:
                logger.error(f"AI transformation failed: {e}")
                return False

        # Apply transformations
        if dry_run:
            patch_file = (
                self.patches_dir
                / f"{plan_type}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.patch"
            )
            self._write_patch_file(patch_file, transformations)
            logger.info(f"Dry run: patch written to {patch_file}")
        else:
            success = self._apply_transformations(transformations)
            if success:
                logger.info("Transformations applied successfully")
                # Run tests after transformation
                self._run_tests()
            return success

        return True

    def _mock_transformations(self, plan_type: str,
                              files: list[Path]) -> dict[str, str]:
        """Create mock transformations for free mode."""
        transformations = {}

        for file_path in files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Simple mock transformations
                if plan_type == "utc_fixes":
                    content = content.replace(
                        "datetime.utcnow()", "datetime.now(timezone.utc)")
                    if "from datetime import" in content and "timezone" not in content:
                        content = content.replace(
                            "from datetime import datetime",
                            "from datetime import datetime, timezone",
                        )

                elif plan_type == "cost_guard_insertion":
                    if "openai" in content.lower() and "eq12_free_guard" not in content:
                        # Add import at top
                        lines = content.split("\n")
                        import_line = "from eq12_free_guard import is_free_mode, get_cost_guards"
                        if import_line not in content:
                            lines.insert(1, import_line)
                        content = "\n".join(lines)

                transformations[str(file_path)] = content

            except Exception as e:
                logger.warning(f"Mock transformation failed for {file_path}: {e}")

        return transformations

    def _parse_ai_response(self, response: str) -> dict[str, str]:
        """Parse AI response into file transformations."""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response

            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Could not parse AI response: {e}")
            return {}

    def _write_patch_file(self, patch_file: Path, transformations: dict[str, str]):
        """Write transformations to a patch file."""
        with open(patch_file, "w", encoding="utf-8") as f:
            f.write(f"# EQ12 Codemod Patch - {datetime.now(UTC).isoformat()}\n\n")
            for file_path, content in transformations.items():
                f.write(f"# File: {file_path}\n")
                f.write("=" * 80 + "\n")
                f.write(content)
                f.write("\n" + "=" * 80 + "\n\n")

    def _apply_transformations(self, transformations: dict[str, str]) -> bool:
        """Apply transformations to files."""
        for file_path, content in transformations.items():
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Applied transformation to {file_path}")
            except Exception as e:
                logger.error(f"Failed to apply transformation to {file_path}: {e}")
                return False
        return True

    def _run_tests(self):
        """Run tests after applying transformations."""
        try:
            # Run ruff check
            subprocess.run(["python", "-m", "ruf", "check", "."], check=False)

            # Run pytest on a subset
            subprocess.run(["python", "-m", "pytest", "tests/",
                           "-x", "--tb=short"], check=False)

            logger.info("Post-transformation tests completed")
        except Exception as e:
            logger.warning(f"Test execution failed: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="EQ12 ChatGPT Codemod System")
    parser.add_argument(
        "--plan",
        required=True,
        choices=[
            "utc_fixes",
            "parlay_sanitizer",
            "cost_guard_insertion",
            "ruff_modernize",
        ],
        help="Codemod plan to execute",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Generate patches without modifying files",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply transformations (overrides --dry-run)",
    )

    args = parser.parse_args()

    system = EQ12CodemodSystem()

    dry_run = args.dry_run and not args.apply

    success = system.execute_codemod(args.plan, dry_run=dry_run)

    if success:
        print(f"✅ Codemod '{args.plan}' completed successfully")
        if dry_run:
            print("   Check logs/patches/ for generated patches")
        else:
            print("   Files modified - run tests to validate")
    else:
        print(f"❌ Codemod '{args.plan}' failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
