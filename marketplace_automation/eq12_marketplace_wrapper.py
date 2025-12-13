#!/usr/bin/env python3
"""
EQ12 Marketplace Automation PowerShell Wrapper
Provides PowerShell integration for marketplace automation tasks
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_powershell_command(command: str, workspace: str = "C:\\EQ12") -> bool:
    """Execute PowerShell command and return success status"""
    try:
        # PowerShell execution command
        ps_cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command]

        logger.info(f" Executing PowerShell: {command}")

        # Run command
        result = subprocess.run(
            ps_cmd, cwd=workspace, capture_output=True, text=True, timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            logger.info(" PowerShell command executed successfully")
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f" PowerShell command failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(" PowerShell command timed out")
        return False
    except Exception as e:
        logger.error(f" PowerShell execution error: {e}")
        return False


def start_marketplace_automation(workspace: str = "C:\\EQ12") -> bool:
    """Start marketplace automation engine"""
    python_script = Path(workspace) / "marketplace_automation" / "eq12_marketplace_scada_engine.py"

    if not python_script.exists():
        logger.error(f" Automation script not found: {python_script}")
        return False

    command = (
        f'Start-Process -FilePath "python" -ArgumentList ""{python_script}"" -WindowStyle Hidden'
    )
    return run_powershell_command(command, workspace)


def start_scada_hmi(workspace: str = "C:\\EQ12") -> bool:
    """Start SCADA HMI dashboard"""
    hmi_exe = (
        Path(workspace)
        / "marketplace_automation"
        / "scada_hmi"
        / "bin"
        / "Release"
        / "EQ12MarketplaceSCADA.exe"
    )

    if not hmi_exe.exists():
        logger.warning(f" HMI executable not found: {hmi_exe}")
        logger.info(" Building HMI from source...")

        # Build HMI project
        project_file = (
            Path(workspace) / "marketplace_automation" / "scada_hmi" / "EQ12MarketplaceSCADA.csproj"
        )
        if project_file.exists():
            build_cmd = f'dotnet build ""{project_file}"" --configuration Release'
            if not run_powershell_command(build_cmd, workspace):
                return False
        else:
            logger.error(" HMI project file not found")
            return False

    command = f'Start-Process -FilePath ""{hmi_exe}"" -WindowStyle Normal'
    return run_powershell_command(command, workspace)


def run_ebay_intelligence(workspace: str = "C:\\EQ12") -> bool:
    """Run eBay intelligence analysis"""
    python_script = Path(workspace) / "marketplace_automation" / "eq12_ebay_intelligence.py"

    if not python_script.exists():
        logger.error(f" eBay intelligence script not found: {python_script}")
        return False

    command = f'python ""{python_script}""'
    return run_powershell_command(command, workspace)


def generate_marketplace_products(workspace: str = "C:\\EQ12") -> bool:
    """Generate marketplace products from EQ12 systems"""
    python_script = Path(workspace) / "marketplace_automation" / "eq12_marketplace_scada_engine.py"

    command = f'python ""{python_script}"" --generate-products'
    return run_powershell_command(command, workspace)


def check_marketplace_status(workspace: str = "C:\\EQ12") -> bool:
    """Check marketplace automation status"""
    commands = [
        'Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -eq "python"}',
        'Get-Process -Name "EQ12MarketplaceSCADA" -ErrorAction SilentlyContinue',
        f'Test-Path ""{Path(workspace) / "data" / "marketplace_automation.db"}""',
    ]

    all_success = True
    for cmd in commands:
        if not run_powershell_command(cmd, workspace):
            all_success = False

    return all_success


def create_marketplace_shortcut(workspace: str = "C:\\EQ12") -> bool:
    """Create desktop shortcut for marketplace automation"""
    shortcut_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\\Desktop\\EQ12 Marketplace SCADA.lnk")
$Shortcut.TargetPath = "python"
$Shortcut.Arguments = '"{Path(workspace) / "marketplace_automation" / "eq12_marketplace_wrapper.py"}" --start-all'
$Shortcut.WorkingDirectory = "{workspace}"
$Shortcut.IconLocation = "{Path(workspace) / "marketplace_automation" / "scada_hmi" / "icon.ico"}"
$Shortcut.Description = "EQ12 Marketplace SCADA Control System"
$Shortcut.Save()
Write-Host " Desktop shortcut created successfully"
"""

    return run_powershell_command(shortcut_script, workspace)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 Marketplace Automation PowerShell Wrapper")
    parser.add_argument(
        "--action",
        choices=[
            "start-automation",
            "start-hmi",
            "start-all",
            "intelligence",
            "generate-products",
            "status",
            "create-shortcut",
        ],
        required=True,
        help="Action to perform",
    )
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")

    args = parser.parse_args()

    logger.info(f" EQ12 Marketplace Automation - Action: {args.action}")

    success = False

    if args.action == "start-automation":
        success = start_marketplace_automation(args.workspace)

    elif args.action == "start-hmi":
        success = start_scada_hmi(args.workspace)

    elif args.action == "start-all":
        logger.info(" Starting complete marketplace automation suite...")
        success = start_marketplace_automation(args.workspace) and start_scada_hmi(args.workspace)

    elif args.action == "intelligence":
        success = run_ebay_intelligence(args.workspace)

    elif args.action == "generate-products":
        success = generate_marketplace_products(args.workspace)

    elif args.action == "status":
        success = check_marketplace_status(args.workspace)

    elif args.action == "create-shortcut":
        success = create_marketplace_shortcut(args.workspace)

    if success:
        logger.info(" Operation completed successfully")
        sys.exit(0)
    else:
        logger.error(" Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
