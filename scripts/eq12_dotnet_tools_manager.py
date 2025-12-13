#!/usr/bin/env python3
"""
EQ12 .NET Tools Manager
Purpose: Download, configure, and manage GitHub .NET development tools
Agent: GitHub Copilot with EQ12 expertise
Timestamp: 2025-10-10T22:00:00Z

Manages:
- dotnet/roslyn (C# and VB compiler platform)
- rubberduck-vba/Rubberduck (VBA code analysis)
- awesome-dotnet (curated .NET resources)
- VS Code VB debugging extensions
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


class EQ12DotNetToolsManager:
    """Comprehensive .NET tools download and configuration manager"""

    def __init__(self, workspace: str = "C:\\\\EQ12"):
        self.workspace = Path(workspace)
        self.tools_dir = self.workspace / "dotnet_tools"
        self.logs_dir = self.workspace / "logs"
        self.configs_dir = self.workspace / "configs"

        # Create directories
        self.tools_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.configs_dir.mkdir(exist_ok=True)

        self.setup_logging()

        # .NET Tools Registry
        self.tools_registry = {
            "roslyn": {
                "name": "Microsoft .NET Compiler Platform (Roslyn)",
                "repo": "dotnet/roslyn",
                "url": "https://github.com/dotnet/roslyn.git",
                "description": "C# and VB compiler platform with analyzers",
                "type": "git_clone",
                "build_required": True,
                "install_path": self.tools_dir / "roslyn",
            },
            "rubberduck": {
                "name": "Rubberduck VBA IDE",
                "repo": "rubberduck-vba/Rubberduck",
                "url": "https://github.com/rubberduck-vba/Rubberduck.git",
                "description": "Advanced VBA debugging, testing, and refactoring",
                "type": "git_clone",
                "build_required": True,
                "install_path": self.tools_dir / "rubberduck",
            },
            "awesome_dotnet": {
                "name": "Awesome .NET Resources",
                "repo": "quozd/awesome-dotnet",
                "url": "https://github.com/quozd/awesome-dotnet.git",
                "description": "Curated list of .NET libraries and tools",
                "type": "git_clone",
                "build_required": False,
                "install_path": self.tools_dir / "awesome-dotnet",
            },
            "vscode_vb_debug": {
                "name": "VS Code VB.NET Debugger",
                "repo": "Microsoft/vscode-vb",
                "url": "https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.vscode-dotnet-runtime",
                "description": "VB.NET debugging support for VS Code",
                "type": "vscode_extension",
                "build_required": False,
                "extension_id": "ms-dotnettools.vscode-dotnet-runtime",
            },
        }

    def setup_logging(self):
        """Configure comprehensive logging"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"dotnet_tools_manager_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🛠️ EQ12 .NET Tools Manager initialized")

    def check_prerequisites(self) -> dict[str, bool]:
        """Check system prerequisites for .NET development"""
        self.logger.info("🔍 Checking system prerequisites...")

        prerequisites = {
            "git": False,
            "dotnet": False,
            "powershell": False,
            "vscode": False,
        }

        # Check Git
        try:
            result = subprocess.run(["git", "--version"],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                prerequisites["git"] = True
                self.logger.info(f"✅ Git found: {result.stdout.strip()}")
        except FileNotFoundError:
            self.logger.warning("❌ Git not found - required for cloning repositories")

        # Check .NET SDK
        try:
            result = subprocess.run(["dotnet", "--version"],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                prerequisites["dotnet"] = True
                self.logger.info(f"✅ .NET SDK found: {result.stdout.strip()}")
        except FileNotFoundError:
            self.logger.warning("❌ .NET SDK not found - required for building tools")

        # Check PowerShell
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Host"], capture_output=True, text=True
            )
            if result.returncode == 0:
                prerequisites["powershell"] = True
                self.logger.info("✅ PowerShell found")
        except FileNotFoundError:
            self.logger.warning("❌ PowerShell not found")

        # Check VS Code
        try:
            result = subprocess.run(["code", "--version"],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                prerequisites["vscode"] = True
                self.logger.info("✅ VS Code found")
        except FileNotFoundError:
            self.logger.info("ℹ️ VS Code not in PATH (may still be installed)")

        return prerequisites

    def download_roslyn(self) -> bool:
        """Download and set up Microsoft Roslyn compiler platform"""
        self.logger.info("📦 Downloading dotnet/roslyn...")

        tool_config = self.tools_registry["roslyn"]
        install_path = tool_config["install_path"]

        try:
            # Clone repository if not exists
            if not install_path.exists():
                self.logger.info(f"🔄 Cloning {tool_config['repo']}...")
                result = subprocess.run(
                    [
                        "git",
                        "clone",
                        "--depth=1",
                        tool_config["url"],
                        str(install_path),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    self.logger.error(f"❌ Failed to clone roslyn: {result.stderr}")
                    return False

                self.logger.info("✅ Roslyn repository cloned successfully")
            else:
                self.logger.info("ℹ️ Roslyn already exists, updating...")
                # Update existing repo
                result = subprocess.run(
                    ["git", "-C", str(install_path), "pull"],
                    capture_output=True,
                    text=True,
                )

            # Check for build requirements
            if (install_path / "Roslyn.sln").exists():
                self.logger.info("🏗️ Roslyn solution file found - ready for building")

                # Create build script
                build_script = install_path / "eq12_build_roslyn.ps1"
                with open(build_script, "w", encoding="utf-8") as f:
                    f.write(
                        """
# EQ12 Roslyn Build Script
Write-Host "🏗️ Building Roslyn Compiler Platform..." -ForegroundColor Green

# Restore packages
dotnet restore Roslyn.sln

# Build solution
dotnet build Roslyn.sln --configuration Release

# Test build
dotnet test --no-build --configuration Release

Write-Host "✅ Roslyn build complete!" -ForegroundColor Green
"""
                    )

                self.logger.info(f"📋 Build script created: {build_script}")

            # Create analyzer configuration
            analyzer_config = install_path / "eq12_roslyn_config.json"
            config = {
                "roslyn_path": str(install_path),
                "analyzers": [
                    "Microsoft.CodeAnalysis.CSharp",
                    "Microsoft.CodeAnalysis.VisualBasic",
                ],
                "usage": {
                    "syntax_analysis": "Analyze C# and VB.NET code syntax",
                    "semantic_analysis": "Type checking and symbol resolution",
                    "code_fixes": "Automated code refactoring and fixes",
                    "diagnostics": "Custom rule enforcement",
                },
            }

            with open(analyzer_config, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            self.logger.info("✅ Roslyn setup complete with EQ12 configuration")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to download Roslyn: {e}")
            return False

    def download_rubberduck(self) -> bool:
        """Download and configure Rubberduck VBA IDE"""
        self.logger.info("🦆 Downloading rubberduck-vba/Rubberduck...")

        tool_config = self.tools_registry["rubberduck"]
        install_path = tool_config["install_path"]

        try:
            # Clone repository
            if not install_path.exists():
                self.logger.info(f"🔄 Cloning {tool_config['repo']}...")
                result = subprocess.run(
                    [
                        "git",
                        "clone",
                        "--depth=1",
                        tool_config["url"],
                        str(install_path),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    self.logger.error(f"❌ Failed to clone Rubberduck: {result.stderr}")
                    return False

                self.logger.info("✅ Rubberduck repository cloned successfully")

            # Check for releases
            releases_info = install_path / "eq12_rubberduck_releases.json"
            try:
                # Get latest release info
                import json
                import urllib.request

                release_url = (
                    "https://api.github.com/repos/rubberduck-vba/Rubberduck/releases/latest"
                )
                with urllib.request.urlopen(release_url) as response:
                    release_data = json.load(response)

                # Save release information
                with open(releases_info, "w", encoding="utf-8") as f:
                    json.dump(release_data, f, indent=2)

                self.logger.info(
                    f"📋 Latest Rubberduck version: {
                        release_data.get(
                            'tag_name', 'unknown')}")

                # Download installer if available
                for asset in release_data.get("assets", []):
                    if asset["name"].endswith(".msi") or asset["name"].endswith(".exe"):
                        installer_url = asset["browser_download_url"]
                        installer_name = asset["name"]
                        installer_path = install_path / installer_name

                        if not installer_path.exists():
                            self.logger.info(
                                f"📥 Downloading installer: {installer_name}")
                            urllib.request.urlretrieve(installer_url, installer_path)
                            self.logger.info(f"✅ Downloaded: {installer_path}")
                        break

            except Exception as e:
                self.logger.warning(f"⚠️ Could not fetch release info: {e}")

            # Create VBA integration guide
            integration_guide = install_path / "eq12_vba_integration_guide.md"
            with open(integration_guide, "w", encoding="utf-8") as f:
                f.write(
                    """# EQ12 Rubberduck VBA Integration Guide

## Installation
1. Run the downloaded .msi installer
2. Open Excel/Word with VBA projects
3. Access Rubberduck via Developer ribbon

## Key Features for EQ12
- **Code Inspections**: Automatically detect VBA issues
- **Unit Testing**: Build test suites for VBA functions
- **Refactoring**: Rename variables, extract methods
- **Source Control**: Git integration for VBA projects

## Usage in EQ12 Workflow
1. Use for Excel automation scripts
2. Debug PowerShell-VBA hybrid solutions
3. Quality assurance for Office automation
4. Integration testing with EQ12 systems

## Configuration
- Enable all code inspections
- Set up unit test framework
- Configure source control integration
- Customize refactoring preferences
"""
                )

            self.logger.info("✅ Rubberduck setup complete with EQ12 integration guide")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to download Rubberduck: {e}")
            return False

    def download_awesome_dotnet(self) -> bool:
        """Download and organize awesome-dotnet resources"""
        self.logger.info("⭐ Downloading awesome-dotnet curated list...")

        tool_config = self.tools_registry["awesome_dotnet"]
        install_path = tool_config["install_path"]

        try:
            # Clone repository
            if not install_path.exists():
                result = subprocess.run(
                    [
                        "git",
                        "clone",
                        "--depth=1",
                        tool_config["url"],
                        str(install_path),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    self.logger.error(
                        f"❌ Failed to clone awesome-dotnet: {result.stderr}")
                    return False

            # Parse README for EQ12-relevant tools
            readme_path = install_path / "README.md"
            if readme_path.exists():
                with open(readme_path, encoding="utf-8") as f:
                    content = f.read()

                # Extract debugging and analysis tools
                eq12_relevant_categories = [
                    "Testing",
                    "Code Analysis",
                    "Logging",
                    "Debugging",
                    "Build Automation",
                    "Profiling",
                    "Visual Studio Plugins",
                ]

                extracted_tools = {}
                current_category = None

                for line in content.split("\n"):
                    # Find category headers
                    if line.startswith("## ") or line.startswith("### "):
                        category = line.strip("# ")
                        if any(cat.lower() in category.lower()
                               for cat in eq12_relevant_categories):
                            current_category = category
                            extracted_tools[category] = []

                    # Extract tool links in relevant categories
                    elif current_category and "](https://github.com/" in line:
                        extracted_tools[current_category].append(line.strip())

                # Save curated EQ12 tools list
                eq12_tools_list = install_path / "eq12_curated_dotnet_tools.json"
                with open(eq12_tools_list, "w", encoding="utf-8") as f:
                    json.dump(extracted_tools, f, indent=2, ensure_ascii=False)

                self.logger.info(f"📋 EQ12 curated tools saved: {eq12_tools_list}")
                self.logger.info(f"📊 Found {len(extracted_tools)} relevant categories")

            self.logger.info("✅ Awesome .NET resources organized for EQ12")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to process awesome-dotnet: {e}")
            return False

    def setup_vscode_vb_debug(self) -> bool:
        """Set up VS Code VB debugging extension"""
        self.logger.info("🔧 Setting up VS Code VB debugging...")

        try:
            # Install .NET runtime extension
            result = subprocess.run(
                ["code", "--install-extension", "ms-dotnettools.vscode-dotnet-runtime"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.logger.info("✅ .NET Runtime extension installed")

            # Install C# extension (includes VB support)
            result = subprocess.run(
                ["code", "--install-extension", "ms-dotnettools.csharp"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.logger.info("✅ C#/VB extension installed")

            # Create VS Code configuration for VB debugging
            vscode_dir = self.workspace / ".vscode"
            vscode_dir.mkdir(exist_ok=True)

            # Launch configuration for VB debugging
            launch_config = vscode_dir / "launch.json"
            existing_config = {}

            if launch_config.exists():
                with open(launch_config, encoding="utf-8") as f:
                    try:
                        existing_config = json.load(f)
                    except BaseException:
                        existing_config = {"version": "0.2.0", "configurations": []}

            # Add VB debugging configuration
            vb_debug_config = {
                "name": "EQ12: Debug VB.NET Application",
                "type": "coreclr",
                "request": "launch",
                "program": "${workspaceFolder}/bin/Debug/net6.0/YourVBApp.dll",
                "args": [],
                "cwd": "${workspaceFolder}",
                "console": "internalConsole",
                "stopAtEntry": False,
            }

            if "configurations" not in existing_config:
                existing_config = {"version": "0.2.0", "configurations": []}

            # Add if not already exists
            config_names = [cfg.get("name", "")
                            for cfg in existing_config["configurations"]]
            if vb_debug_config["name"] not in config_names:
                existing_config["configurations"].append(vb_debug_config)

            with open(launch_config, "w", encoding="utf-8") as f:
                json.dump(existing_config, f, indent=2)

            self.logger.info(f"✅ VS Code VB debug configuration saved: {launch_config}")

            # Create VB project template
            vb_template_dir = self.tools_dir / "vb_project_template"
            vb_template_dir.mkdir(exist_ok=True)

            vb_project_file = vb_template_dir / "EQ12VBProject.vbproj"
            with open(vb_project_file, "w", encoding="utf-8") as f:
                f.write(
                    """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net6.0</TargetFramework>
    <RootNamespace>EQ12VBProject</RootNamespace>
  </PropertyGroup>
</Project>"""
                )

            vb_main_file = vb_template_dir / "Program.vb"
            with open(vb_main_file, "w", encoding="utf-8") as f:
                f.write(
                    """Imports System

Module Program
    Sub Main(args As String())
        ' EQ12 VB.NET Application Template
        Console.WriteLine("🚀 EQ12 VB.NET Application Started")

        ' Your VB.NET code here
        Console.WriteLine("✅ Application completed successfully")
    End Sub
End Module"""
                )

            self.logger.info(f"✅ VB project template created: {vb_template_dir}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to setup VS Code VB debugging: {e}")
            return False

    def download_all_tools(self) -> dict[str, bool]:
        """Download and set up all .NET development tools"""
        self.logger.info("🚀 Starting comprehensive .NET tools download...")

        # Check prerequisites first
        prerequisites = self.check_prerequisites()
        if not prerequisites.get("git", False):
            self.logger.error(
                "❌ Git is required but not found. Please install Git first.")
            return {}

        results = {}

        # Download each tool
        results["roslyn"] = self.download_roslyn()
        results["rubberduck"] = self.download_rubberduck()
        results["awesome_dotnet"] = self.download_awesome_dotnet()
        results["vscode_vb_debug"] = self.setup_vscode_vb_debug()

        # Generate comprehensive report
        self.generate_tools_report(results)

        return results

    def generate_tools_report(self, results: dict[str, bool]):
        """Generate comprehensive .NET tools installation report"""
        timestamp = datetime.now(UTC).isoformat()

        report = {
            "timestamp": timestamp,
            "workspace": str(self.workspace),
            "tools_directory": str(self.tools_dir),
            "installation_results": results,
            "tools_summary": {},
            "next_steps": [],
            "troubleshooting": {},
        }

        # Add tool summaries
        for tool_name, success in results.items():
            tool_config = self.tools_registry.get(tool_name, {})
            report["tools_summary"][tool_name] = {
                "name": tool_config.get("name", tool_name),
                "status": "✅ Installed" if success else "❌ Failed",
                "description": tool_config.get("description", ""),
                "path": str(tool_config.get("install_path", "")),
            }

        # Add next steps
        if results.get("roslyn", False):
            report["next_steps"].append(
                "Build Roslyn: Run eq12_build_roslyn.ps1 in roslyn directory"
            )

        if results.get("rubberduck", False):
            report["next_steps"].append(
                "Install Rubberduck: Run the downloaded .msi installer")

        if results.get("vscode_vb_debug", False):
            report["next_steps"].append(
                "Test VB debugging: Create new VB project and use F5 to debug"
            )

        # Save report
        report_file = (
            self.logs_dir /
            f"dotnet_tools_report_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"📊 Comprehensive report saved: {report_file}")

        # Print summary
        successful_tools = [name for name, success in results.items() if success]
        failed_tools = [name for name, success in results.items() if not success]

        self.logger.info(f"✅ Successfully installed: {len(successful_tools)} tools")
        self.logger.info(f"❌ Failed installations: {len(failed_tools)} tools")

        if successful_tools:
            self.logger.info(f"🎉 Ready to use: {', '.join(successful_tools)}")

        if failed_tools:
            self.logger.warning(f"⚠️ Retry needed: {', '.join(failed_tools)}")


def main():
    """Main entry point for EQ12 .NET Tools Manager"""
    parser = argparse.ArgumentParser(
        description="EQ12 .NET Development Tools Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --download-all                    # Download all .NET tools
  %(prog)s --tool roslyn                     # Download Roslyn only
  %(prog)s --tool rubberduck                 # Download Rubberduck only
  %(prog)s --check-prerequisites             # Check system requirements
  %(prog)s --workspace "D:\\MyProject"       # Use custom workspace
        """,
    )

    parser.add_argument(
        "--workspace",
        default="C:\\\\EQ12",
        help="EQ12 workspace directory (default: C:\\\\EQ12)",
    )
    parser.add_argument(
        "--download-all",
        action="store_true",
        help="Download and set up all .NET development tools",
    )
    parser.add_argument(
        "--tool",
        choices=["roslyn", "rubberduck", "awesome_dotnet", "vscode_vb_debug"],
        help="Download specific tool only",
    )
    parser.add_argument(
        "--check-prerequisites",
        action="store_true",
        help="Check system prerequisites for .NET development",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        manager = EQ12DotNetToolsManager(args.workspace)

        if args.check_prerequisites:
            print("🔍 EQ12 .NET Development Prerequisites Check")
            print("=" * 50)
            prerequisites = manager.check_prerequisites()
            for tool, available in prerequisites.items():
                status = "✅ Available" if available else "❌ Missing"
                print(f"{tool:12} - {status}")
            print("=" * 50)

        elif args.download_all:
            print("🚀 EQ12 Comprehensive .NET Tools Download")
            print("=" * 50)
            manager.download_all_tools()
            print("=" * 50)
            print("✅ Process completed! Check logs for details.")

        elif args.tool:
            print(f"📦 Downloading {args.tool}...")
            if args.tool == "roslyn":
                success = manager.download_roslyn()
            elif args.tool == "rubberduck":
                success = manager.download_rubberduck()
            elif args.tool == "awesome_dotnet":
                success = manager.download_awesome_dotnet()
            elif args.tool == "vscode_vb_debug":
                success = manager.setup_vscode_vb_debug()

            status = "✅ Success" if success else "❌ Failed"
            print(f"{args.tool}: {status}")

        else:
            parser.print_help()

    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
