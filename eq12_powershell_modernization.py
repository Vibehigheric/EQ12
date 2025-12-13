# eq12_powershell_modernization.py
"""
EQ12 PowerShell 7+ Modernization System
UTF-8 console handling, environment management, automated script repair
"""

import asyncio
import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from eq12_helpers import setup_utf8_logging

setup_utf8_logging()


@dataclass
class PowerShellEnvironment:
    """PowerShell environment configuration"""

    version: str
    path: str
    modules: list[str]
    execution_policy: str
    profile_path: str | None = None
    is_core: bool = False


@dataclass
class ScriptAnalysis:
    """PowerShell script analysis result"""

    file_path: Path
    version_compatibility: str
    issues_found: list[str]
    suggestions: list[str]
    modernization_needed: bool
    confidence_score: float


class PowerShellEnvironmentManager:
    """Advanced PowerShell environment management"""

    def __init__(self):
        self.detected_environments: list[PowerShellEnvironment] = []
        self.active_environment: PowerShellEnvironment | None = None

    async def detect_powershell_environments(self) -> list[PowerShellEnvironment]:
        """Detect all PowerShell installations"""

        environments = []

        # Check for PowerShell 7+ (Core)
        pwsh_paths = [
            r"C:\Program Files\PowerShell\7\pwsh.exe",
            r"C:\Program Files (x86)\PowerShell\7\pwsh.exe",
            "pwsh.exe",  # In PATH
        ]

        for pwsh_path in pwsh_paths:
            try:
                result = await self._run_powershell_command(
                    pwsh_path, "$PSVersionTable.PSVersion.ToString()"
                )
                if result.returncode == 0:
                    version = result.stdout.decode("utf-8").strip()

                    # Get modules
                    modules_result = await self._run_powershell_command(
                        pwsh_path,
                        "Get-Module -ListAvailable | Select-Object Name | ConvertTo-Json",
                    )

                    modules = []
                    if modules_result.returncode == 0:
                        try:
                            modules_data = json.loads(modules_result.stdout.decode("utf-8"))
                            if isinstance(modules_data, list):
                                modules = [m["Name"] for m in modules_data]
                            elif isinstance(modules_data, dict):
                                modules = [modules_data["Name"]]
                        except:
                            pass

                    # Get execution policy
                    policy_result = await self._run_powershell_command(
                        pwsh_path, "Get-ExecutionPolicy"
                    )

                    policy = "Unknown"
                    if policy_result.returncode == 0:
                        policy = policy_result.stdout.decode("utf-8").strip()

                    environments.append(
                        PowerShellEnvironment(
                            version=version,
                            path=pwsh_path,
                            modules=modules,
                            execution_policy=policy,
                            is_core=True,
                        )
                    )
                    break
            except:
                continue

        # Check for Windows PowerShell 5.1
        powershell_paths = [
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "powershell.exe",  # In PATH
        ]

        for ps_path in powershell_paths:
            try:
                result = await self._run_powershell_command(
                    ps_path, "$PSVersionTable.PSVersion.ToString()"
                )
                if result.returncode == 0:
                    version = result.stdout.decode("utf-8").strip()

                    # Get execution policy
                    policy_result = await self._run_powershell_command(
                        ps_path, "Get-ExecutionPolicy"
                    )

                    policy = "Unknown"
                    if policy_result.returncode == 0:
                        policy = policy_result.stdout.decode("utf-8").strip()

                    environments.append(
                        PowerShellEnvironment(
                            version=version,
                            path=ps_path,
                            modules=[],
                            execution_policy=policy,
                            is_core=False,
                        )
                    )
                    break
            except:
                continue

        self.detected_environments = environments
        return environments

    async def _run_powershell_command(
        self, executable: str, command: str
    ) -> subprocess.CompletedProcess:
        """Run PowerShell command and return result"""

        cmd_args = [
            executable,
            "-NoProfile",
            "-NonInteractive",
            "-OutputFormat",
            "Text",
            "-Command",
            command,
        ]

        return await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        ).communicate()

    def select_best_environment(self) -> PowerShellEnvironment | None:
        """Select the best PowerShell environment"""

        if not self.detected_environments:
            return None

        # Prefer PowerShell 7+ over Windows PowerShell
        core_envs = [env for env in self.detected_environments if env.is_core]
        if core_envs:
            # Select newest version
            core_envs.sort(key=lambda x: x.version, reverse=True)
            self.active_environment = core_envs[0]
            return self.active_environment

        # Fallback to Windows PowerShell
        legacy_envs = [env for env in self.detected_environments if not env.is_core]
        if legacy_envs:
            self.active_environment = legacy_envs[0]
            return self.active_environment

        return None

    async def setup_utf8_console(self):
        """Setup UTF-8 console encoding"""

        if not self.active_environment:
            return False

        utf8_setup_command = """
        # Set console encoding to UTF-8
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        [Console]::InputEncoding = [System.Text.Encoding]::UTF8

        # Set PowerShell output encoding
        $OutputEncoding = [System.Text.Encoding]::UTF8

        Write-Output "UTF-8 encoding configured successfully"
        """

        try:
            result = await self._run_powershell_command(
                self.active_environment.path, utf8_setup_command
            )

            return result.returncode == 0
        except:
            return False


class PowerShellScriptAnalyzer:
    """Analyze and modernize PowerShell scripts"""

    def __init__(self):
        self.modernization_patterns = {
            # Cmdlet binding improvements
            r"\[CmdletBinding\(\)\]": {
                "replacement": "[CmdletBinding(SupportsShouldProcess = $true)]",
                "description": "Add SupportsShouldProcess for better practices",
            },
            # Parameter validation
            r"param\s*\(\s*\$(\w+)\s*\)": {
                "replacement": "param(\n    [Parameter(Mandatory = $true)]\n    [ValidateNotNullOrEmpty()]\n    [string]$\\1\n)",
                "description": "Add parameter validation",
            },
            # Error handling improvements
            r'Write-Host\s+"([^"]*)"': {
                "replacement": 'Write-Information "\\1" -InformationAction Continue',
                "description": "Use Write-Information instead of Write-Host",
            },
            # UTF-8 encoding
            r"Out-File\s+-FilePath\s+([^\s]+)": {
                "replacement": "Out-File -FilePath \\1 -Encoding UTF8",
                "description": "Ensure UTF-8 encoding for file output",
            },
            # Modern operators
            r"-eq\s+\$null": {
                "replacement": "-is [System.DBNull] -or $null -eq",
                "description": "Use proper null comparison",
            },
            # Splatting improvements
            r"\$(\w+)\s*=\s*@{": {
                "replacement": "$\\1Parameters = @{",
                "description": "Use descriptive splatting variable names",
            },
        }

        self.compatibility_checks = {
            "Windows PowerShell 5.1": [
                r"Import-Module\s+Microsoft\.PowerShell\.Archive",
                r"Compress-Archive",
                r"Expand-Archive",
            ],
            "PowerShell 7+": [
                r"ForEach-Object\s+-Parallel",
                r"Test-Json",
                r"ConvertFrom-Json\s+-AsHashtable",
            ],
        }

    async def analyze_script(self, script_path: Path) -> ScriptAnalysis:
        """Analyze PowerShell script for modernization opportunities"""

        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        content = script_path.read_text(encoding="utf-8")

        issues_found = []
        suggestions = []
        confidence_score = 1.0

        # Check for common issues

        # 1. Encoding issues
        if "Out-File" in content and "-Encoding" not in content:
            issues_found.append("Missing explicit encoding in Out-File commands")
            suggestions.append("Add -Encoding UTF8 to Out-File commands")
            confidence_score -= 0.1

        # 2. Error handling
        if "try" not in content.lower() and "catch" not in content.lower():
            if len(content) > 500:  # Only for substantial scripts
                issues_found.append("No error handling detected")
                suggestions.append("Add try-catch blocks for robust error handling")
                confidence_score -= 0.15

        # 3. Parameter validation
        if "param(" in content and "[Parameter(" not in content:
            issues_found.append("Parameters lack validation attributes")
            suggestions.append("Add [Parameter()] attributes with validation")
            confidence_score -= 0.1

        # 4. CmdletBinding
        if "function " in content and "[CmdletBinding()]" not in content:
            issues_found.append("Functions missing [CmdletBinding()]")
            suggestions.append("Add [CmdletBinding()] to functions")
            confidence_score -= 0.1

        # 5. Write-Host usage
        write_host_count = len(re.findall(r"Write-Host", content, re.IGNORECASE))
        if write_host_count > 0:
            issues_found.append(f"Found {write_host_count} Write-Host usages")
            suggestions.append("Consider using Write-Information, Write-Verbose, or Write-Output")
            confidence_score -= 0.05 * write_host_count

        # Determine version compatibility
        version_compatibility = self._check_version_compatibility(content)

        # Determine if modernization is needed
        modernization_needed = len(issues_found) > 0 or confidence_score < 0.8

        return ScriptAnalysis(
            file_path=script_path,
            version_compatibility=version_compatibility,
            issues_found=issues_found,
            suggestions=suggestions,
            modernization_needed=modernization_needed,
            confidence_score=max(0.0, confidence_score),
        )

    def _check_version_compatibility(self, content: str) -> str:
        """Check PowerShell version compatibility"""

        # Check for PowerShell 7+ specific features
        ps7_patterns = [
            r"ForEach-Object\s+-Parallel",
            r"Test-Json",
            r"ConvertFrom-Json\s+-AsHashtable",
            r"null\s*\?\?\s*",  # Null coalescing operator
            r"\?\?\=",  # Null assignment operator
        ]

        for pattern in ps7_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return "PowerShell 7+ Required"

        # Check for Windows PowerShell 5.1 specific features
        ps51_patterns = [
            r"Import-Module\s+Microsoft\.PowerShell\.Archive",
            r"Compress-Archive",
            r"Expand-Archive",
        ]

        for pattern in ps51_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return "Windows PowerShell 5.1+"

        return "PowerShell 3.0+"

    async def modernize_script(self, script_path: Path, backup: bool = True) -> dict[str, Any]:
        """Modernize PowerShell script"""

        if backup:
            backup_path = script_path.with_suffix(
                f"{script_path.suffix}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            backup_path.write_text(script_path.read_text(encoding="utf-8"), encoding="utf-8")

        content = script_path.read_text(encoding="utf-8")
        original_content = content

        modifications = []

        # Apply modernization patterns
        for pattern, replacement_info in self.modernization_patterns.items():
            old_content = content
            content = re.sub(pattern, replacement_info["replacement"], content, flags=re.MULTILINE)

            if content != old_content:
                modifications.append(replacement_info["description"])

        # Write modernized script
        if content != original_content:
            script_path.write_text(content, encoding="utf-8")

        return {
            "modified": content != original_content,
            "modifications": modifications,
            "backup_created": backup,
            "backup_path": str(backup_path) if backup else None,
        }


class PowerShellTaskAutomation:
    """Automated PowerShell task management"""

    def __init__(self, env_manager: PowerShellEnvironmentManager):
        self.env_manager = env_manager

    async def create_scheduled_task(
        self,
        task_name: str,
        script_path: Path,
        schedule: str = "Daily",
        start_time: str = "09:00",
    ) -> bool:
        """Create Windows scheduled task for PowerShell script"""

        if not self.env_manager.active_environment:
            return False

        # PowerShell command to create scheduled task
        create_task_command = f"""
        $Action = New-ScheduledTaskAction -Execute "{self.env_manager.active_environment.path}" -Argument "-NoProfile -ExecutionPolicy Bypass -File '{script_path}'"

        $Trigger = New-ScheduledTaskTrigger -Daily -At "{start_time}"

        $Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest

        $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

        $Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "EQ12 Automated Task: {task_name}"

        try {{
            Register-ScheduledTask -TaskName "EQ12_{task_name}" -InputObject $Task -Force
            Write-Output "SUCCESS"
        }} catch {{
            Write-Output "FAILED: $($_.Exception.Message)"
        }}
        """

        try:
            result = await self.env_manager._run_powershell_command(
                self.env_manager.active_environment.path, create_task_command
            )

            output = result.stdout.decode("utf-8").strip()
            return "SUCCESS" in output

        except Exception as e:
            logging.error(f"Failed to create scheduled task: {e}")
            return False

    async def install_required_modules(self, modules: list[str]) -> dict[str, bool]:
        """Install required PowerShell modules"""

        if not self.env_manager.active_environment:
            return {}

        results = {}

        for module in modules:
            install_command = f"""
            try {{
                if (!(Get-Module -ListAvailable -Name {module})) {{
                    Install-Module -Name {module} -Force -AllowClobber -Scope CurrentUser
                    Write-Output "INSTALLED_{module}"
                }} else {{
                    Write-Output "EXISTS_{module}"
                }}
            }} catch {{
                Write-Output "FAILED_{module}: $($_.Exception.Message)"
            }}
            """

            try:
                result = await self.env_manager._run_powershell_command(
                    self.env_manager.active_environment.path, install_command
                )

                output = result.stdout.decode("utf-8").strip()
                results[module] = "INSTALLED" in output or "EXISTS" in output

            except:
                results[module] = False

        return results


async def main():
    """Demonstrate PowerShell modernization system"""

    setup_utf8_logging()
    logging.info("🔧 Starting PowerShell 7+ Modernization System")

    # Initialize environment manager
    env_manager = PowerShellEnvironmentManager()

    # Detect PowerShell environments
    environments = await env_manager.detect_powershell_environments()

    print("✅ Detected {len(environments)} PowerShell environments:")
    for _env in environments:
        print("   - {env.version} ({core_status}) - {env.execution_policy}")

    # Select best environment
    best_env = env_manager.select_best_environment()
    if best_env:
        print("🎯 Selected: {best_env.version} ({best_env.path})")

        # Setup UTF-8 console
        await env_manager.setup_utf8_console()
        print("🔤 UTF-8 Console: {'Configured' if utf8_success else 'Failed'}")
    else:
        print("❌ No PowerShell environment found")
        return

    # Initialize script analyzer
    analyzer = PowerShellScriptAnalyzer()

    # Analyze sample script (if exists)
    scripts_to_analyze = [
        Path(r"C:\EQ12\scripts\bootstrap_eq12.ps1"),
        Path(r"C:\EQ12\eq12_status_check_clean.ps1"),
    ]

    for script_path in scripts_to_analyze:
        if script_path.exists():
            analysis = await analyzer.analyze_script(script_path)

            print("\n📋 Analysis: {script_path.name}")
            print("   Compatibility: {analysis.version_compatibility}")
            print("   Confidence: {analysis.confidence_score:.2f}")
            print("   Modernization needed: {analysis.modernization_needed}")

            if analysis.issues_found:
                print("   Issues:")
                for _issue in analysis.issues_found:
                    print("     - {issue}")

    # Initialize task automation
    task_automation = PowerShellTaskAutomation(env_manager)

    # Install common modules
    required_modules = ["PSScriptAnalyzer", "Pester"]
    install_results = await task_automation.install_required_modules(required_modules)

    print("\n📦 Module Installation:")
    for _module, _success in install_results.items():
        print("   {status} {module}")

    print("\n🎉 PowerShell Modernization System Ready!")


if __name__ == "__main__":
    asyncio.run(main())
