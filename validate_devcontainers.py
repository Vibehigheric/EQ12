#!/usr/bin/env python3
"""
EQ12 Devcontainer Validation and Testing Script
Validates all devcontainer configurations and tests functionality
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class DevcontainerValidator:
    """Validates devcontainer configurations"""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.validation_results = []

    def validate_all_configs(self) -> bool:
        """Validate all devcontainer configurations"""
        logger.info("🔍 Starting devcontainer validation...")

        configs = list(self.repo_root.rglob("**/devcontainer.json"))
        if not configs:
            logger.error("❌ No devcontainer.json files found")
            return False

        logger.info(f"Found {len(configs)} devcontainer configurations")

        all_valid = True
        for config_file in configs:
            if not self._validate_single_config(config_file):
                all_valid = False

        return all_valid

    def _validate_single_config(self, config_file: Path) -> bool:
        """Validate a single devcontainer configuration"""
        logger.info(f"Validating {config_file.relative_to(self.repo_root)}")

        try:
            # Test JSON parsing
            with open(config_file, encoding="utf-8") as f:
                content = f.read()

            # Remove comments for validation
            clean_content = self._remove_json_comments(content)
            config = json.loads(clean_content)

            # Validate required fields
            required_fields = ["name", "image"]
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                logger.error(f"❌ Missing required fields: {missing_fields}")
                return False

            # Validate image format
            image = config.get("image", "")
            if not image.startswith("mcr.microsoft.com/devcontainers/"):
                logger.warning(f"⚠️ Non-standard base image: {image}")

            # Check for security issues
            if self._check_security_config(config):
                logger.warning("⚠️ Potential security issues detected")

            # Validate post-create script exists
            post_create = config.get("postCreateCommand", "")
            if post_create and ".ps1" in post_create:
                script_path = config_file.parent / "postCreate.ps1"
                if not script_path.exists():
                    script_path = config_file.parent / "post_create.ps1"
                if not script_path.exists():
                    logger.error(f"❌ Post-create script not found: {post_create}")
                    return False

            logger.info(f"✅ {config_file.name} is valid")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON syntax error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False

    def _remove_json_comments(self, content: str) -> str:
        """Remove JSON comments for validation"""
        import re

        # Remove // comments
        content = re.sub(r"//.*", "", content)
        # Remove /* */ comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        # Remove _comment properties
        content = re.sub(r'"_comment"\s*:\s*"[^"]*",?\s*', "", content)
        return content

    def _check_security_config(self, config: dict) -> bool:
        """Check for security issues in configuration"""
        issues = []

        # Check for privileged containers
        run_args = config.get("runArgs", [])
        if "--privileged" in str(run_args):
            issues.append("Privileged container detected")

        # Check for docker socket mounts
        mounts = config.get("mounts", [])
        for mount in mounts:
            if "docker.sock" in str(mount):
                issues.append("Docker socket mount detected")

        # Check for missing remote user
        if not config.get("remoteUser"):
            issues.append("No remoteUser specified")

        if issues:
            logger.warning(f"Security issues: {', '.join(issues)}")
            return True
        return False

    def test_devcontainer_build(self, config_path: Path) -> bool:
        """Test building a devcontainer"""
        logger.info(f"🔨 Testing build for {config_path}")

        try:
            # Check if devcontainer CLI is available
            result = subprocess.run(
                ["devcontainer", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.error("❌ devcontainer CLI not available")
                return False

            # Test build (dry run)
            workspace_folder = config_path.parent.parent
            result = subprocess.run(
                [
                    "devcontainer",
                    "build",
                    "--workspace-folder",
                    str(workspace_folder),
                    "--log-level",
                    "info",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                logger.info("✅ Devcontainer build test passed")
                return True
            logger.error(f"❌ Build failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Build test timed out")
            return False
        except FileNotFoundError:
            logger.warning("⚠️ devcontainer CLI not found, skipping build test")
            return True
        except Exception as e:
            logger.error(f"❌ Build test failed: {e}")
            return False


def main():
    """Main validation function"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate EQ12 devcontainer configurations")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--test-build", action="store_true", help="Test devcontainer builds")

    args = parser.parse_args()

    validator = DevcontainerValidator(args.repo_root)

    # Validate configurations
    valid = validator.validate_all_configs()

    # Test builds if requested
    if args.test_build:
        configs = list(Path(args.repo_root).rglob("**/devcontainer.json"))
        for config in configs:
            validator.test_devcontainer_build(config)

    if valid:
        logger.info("🎉 All devcontainer configurations are valid!")
        sys.exit(0)
    else:
        logger.error("❌ Some devcontainer configurations have issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
