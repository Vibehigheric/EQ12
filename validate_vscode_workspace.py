#!/usr/bin/env python3
"""
EQ12 GODSTACK - VS Code Workspace Validation Script
Validates all workspace configurations and reports system readiness.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Configure logging for workspace validation."""
    log_dir = Path("C:/EQ12/logs") if os.name == "nt" else Path("/workspaces/EQ12/logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "vscode_workspace_validation.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def validate_vscode_config():
    """Validate VS Code workspace configuration files."""
    logger = logging.getLogger(__name__)
    vscode_dir = Path(".vscode")

    required_files = {
        "settings.json": "VS Code settings configuration",
        "tasks.json": "Custom EQ12 automation tasks",
        "launch.json": "Debug configurations",
        "extensions.json": "Recommended extensions pack",
    }

    results = {}

    for file_name, description in required_files.items():
        file_path = vscode_dir / file_name
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = json.load(f)
                results[file_name] = {
                    "status": "✅ Valid",
                    "description": description,
                    "size": file_path.stat().st_size,
                    "keys": (list(content.keys()) if isinstance(content, dict) else len(content)),
                }
                logger.info(f"✅ {file_name}: Valid JSON configuration")
            except json.JSONDecodeError as e:
                results[file_name] = {
                    "status": "❌ Invalid JSON",
                    "description": description,
                    "error": str(e),
                }
                logger.error(f"❌ {file_name}: Invalid JSON - {e}")
            except Exception as e:
                results[file_name] = {
                    "status": "❌ Error",
                    "description": description,
                    "error": str(e),
                }
                logger.error(f"❌ {file_name}: Error reading file - {e}")
        else:
            results[file_name] = {"status": "❌ Missing", "description": description}
            logger.warning(f"❌ {file_name}: File missing")

    return results


def check_workspace_file():
    """Check for workspace file configuration."""
    logger = logging.getLogger(__name__)
    workspace_file = Path("EQ12-GODSTACK.code-workspace")

    if workspace_file.exists():
        try:
            with open(workspace_file, encoding="utf-8") as f:
                content = json.load(f)

            folders = content.get("folders", [])
            settings = content.get("settings", {})
            extensions = content.get("extensions", {})

            logger.info(f"✅ Workspace file: {len(folders)} folders configured")
            return {
                "status": "✅ Valid",
                "folders": len(folders),
                "settings": len(settings),
                "extensions": len(extensions.get("recommendations", [])),
            }
        except Exception as e:
            logger.error(f"❌ Workspace file: Error reading - {e}")
            return {"status": "❌ Invalid", "error": str(e)}
    else:
        logger.warning("❌ Workspace file: Missing")
        return {"status": "❌ Missing"}


def check_python_environment():
    """Check Python environment configuration."""
    logger = logging.getLogger(__name__)

    python_info = {
        "version": sys.version,
        "executable": sys.executable,
        "path": sys.path[:3],  # First 3 path entries
        "platform": sys.platform,
    }

    # Check for virtual environment
    venv_path = Path(".venv")
    if venv_path.exists():
        python_info["virtual_env"] = "✅ Present"
        logger.info("✅ Python virtual environment detected")
    else:
        python_info["virtual_env"] = "⚠️ Not detected"
        logger.warning("⚠️ Python virtual environment not detected")

    # Check for requirements.txt
    req_file = Path("requirements.txt")
    if req_file.exists():
        python_info["requirements"] = "✅ Present"
        logger.info("✅ Requirements file found")
    else:
        python_info["requirements"] = "⚠️ Missing"
        logger.warning("⚠️ Requirements file not found")

    return python_info


def generate_report():
    """Generate comprehensive validation report."""
    logger = logging.getLogger(__name__)

    print("\n" + "=" * 60)
    print("🚀 EQ12 GODSTACK - VS Code Workspace Validation Report")
    print("=" * 60)

    # VS Code Configuration
    print("\n📁 VS Code Configuration:")
    vscode_results = validate_vscode_config()
    for file_name, result in vscode_results.items():
        status = result["status"]
        description = result["description"]
        print(f"   {status} {file_name}: {description}")
        if "size" in result:
            print(f"      Size: {result['size']:,} bytes, Keys: {result['keys']}")
        if "error" in result:
            print(f"      Error: {result['error']}")

    # Workspace File
    print("\n🏗️ Workspace Configuration:")
    workspace_result = check_workspace_file()
    print(f"   {workspace_result['status']} EQ12-GODSTACK.code-workspace")
    if "folders" in workspace_result:
        print(
            f"      Folders: {workspace_result['folders']}, Settings: {workspace_result['settings']}, Extensions: {workspace_result['extensions']}"
        )

    # Python Environment
    print("\n🐍 Python Environment:")
    python_info = check_python_environment()
    print(f"   ✅ Python Version: {python_info['version'].split()[0]}")
    print(f"   ✅ Executable: {python_info['executable']}")
    print(f"   {python_info['virtual_env']} Virtual Environment")
    print(f"   {python_info['requirements']} Requirements File")

    # Summary
    print("\n📊 Summary:")
    all_valid = all(
        result["status"].startswith("✅") for result in vscode_results.values()
    ) and workspace_result["status"].startswith("✅")

    if all_valid:
        print("   ✅ All configurations valid - Workspace ready!")
        logger.info("🎉 EQ12 GODSTACK workspace validation successful")
    else:
        print("   ⚠️ Some configurations need attention")
        logger.warning("⚠️ EQ12 GODSTACK workspace validation found issues")

    # Usage Instructions
    print("\n🎯 Next Steps:")
    print("   1. Open workspace: code EQ12-GODSTACK.code-workspace")
    print("   2. Install extensions when prompted")
    print("   3. Run task: Ctrl+Shift+P → 'EQ12: Status Check'")
    print("   4. Start debugging: F5 → 'EQ12: Quick Start'")

    print("\n" + "=" * 60)

    return all_valid


if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Starting EQ12 GODSTACK workspace validation")

    try:
        success = generate_report()

        # Save validation snapshot
        timestamp = datetime.utcnow().isoformat() + "Z"
        snapshot = {
            "timestamp": timestamp,
            "validation_success": success,
            "python_version": sys.version,
            "workspace_directory": str(Path.cwd()),
            "validator_version": "1.0.0",
        }

        log_dir = Path("C:/EQ12/logs") if os.name == "nt" else Path("/workspaces/EQ12/logs")
        snapshot_file = (
            log_dir / f"workspace_validation_{timestamp.replace(':', '-').replace('.', '-')}.json"
        )

        with open(snapshot_file, "w") as f:
            json.dump(snapshot, f, indent=2)

        logger.info(f"Validation snapshot saved: {snapshot_file}")

        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)
