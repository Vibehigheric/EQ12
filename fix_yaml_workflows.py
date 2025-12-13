#!/usr/bin/env python3
"""
Quick fix for corrupted YAML workflows
"""

import shutil
from pathlib import Path


def fix_workflow_yaml(file_path: Path):
    """Fix corrupted YAML workflow files"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Create backup
        backup_path = file_path.with_suffix(f"{file_path.suffix}.corrupt_backup")
        shutil.copy2(file_path, backup_path)

        # Fix the corrupted patterns
        lines = content.split("\n")
        fixed_lines = []
        skip_next = False

        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue

            # Fix duplicate runs-on lines
            if "runs-on:" in line and i < len(lines) - 1:
                # Check if next few lines are also runs-on or permissions
                j = i + 1
                while j < len(lines) and (
                    "runs-on:" in lines[j]
                    or lines[j].strip() in ["permissions:", "contents: read"]
                    or lines[j].strip() == ""
                ):
                    j += 1

                # Keep the first runs-on, add proper permissions after it
                fixed_lines.append(line)
                fixed_lines.append("    permissions:")
                fixed_lines.append("      contents: read")

                # Skip the corrupted lines
                i = j - 1
                continue

            fixed_lines.append(line)

        # Write fixed content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(fixed_lines))

        print(f"Fixed {file_path.name}")
        return True

    except Exception as e:
        print(f"Error fixing {file_path.name}: {e}")
        return False


# Fix all corrupted workflow files
workflows_dir = Path("C:/EQ12/.github/workflows")
corrupted_files = [
    "eq12-nightly.yml",
    "eq12-daily.yml",
    "eq12-ci.yml",
    "eq12-codex.yml",
    "eq12-daily-run.yml",
    "eq12-guardian.yml",
    "eq12-ngrok.yml",
    "graphic_alerts.yml",
    "ngrok-test.yml",
    "travel-deals.yml",
    "wireguard-tunnel.yml",
    "codespaces-extensions.yml",
    "codespaces-setup.yml",
]

print("Fixing corrupted YAML workflow files...")
for filename in corrupted_files:
    file_path = workflows_dir / filename
    if file_path.exists():
        fix_workflow_yaml(file_path)

print("YAML fixes complete!")
