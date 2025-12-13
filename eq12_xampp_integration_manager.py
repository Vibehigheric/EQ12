"""
EQ12 XAMPP Source Code Integration Manager
=========================================

Professional XAMPP source code management for the EQ12 tri-language betting platform.
Integrates XAMPP source with Python AI, Node.js real-time, and PHP web capabilities.

Features:
- SVN installation validation and setup
- XAMPP source code checkout and management
- Custom EQ12 XAMPP build configuration
- Integration with existing tri-language platform
- Enterprise deployment preparation

Author: EQ12 Development Team
Version: 1.0.0
License: MIT
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class EQ12XAMPPIntegrationManager:
    """
    Professional XAMPP source code integration manager for EQ12 platform.

    Manages SVN operations, source code checkout, custom builds, and
    integration with the existing tri-language betting platform.
    """

    def __init__(self, eq12_root: str = "C:\\EQ12"):
        """Initialize the XAMPP Integration Manager."""
        self.eq12_root = Path(eq12_root)
        self.xampp_dev_dir = self.eq12_root / "xampp-dev"
        self.xampp_custom_dir = self.eq12_root / "xampp-custom"
        self.logs_dir = self.eq12_root / "logs"
        self.configs_dir = self.eq12_root / "configs"

        # Ensure directories exist
        for directory in [self.xampp_dev_dir, self.xampp_custom_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)

        # Setup logging
        self.setup_logging()

        # XAMPP source URLs
        self.xampp_svn_urls = {
            "main": "https://svn.code.sf.net/p/xampp/code/",
            "trunk": "https://svn.code.sf.net/p/xampp/code/trunk",
            "branches": "https://svn.code.sf.net/p/xampp/code/branches",
            "tags": "https://svn.code.sf.net/p/xampp/code/tags",
        }

        # Component-specific URLs
        self.component_urls = {
            "apache": "https://svn.code.sf.net/p/xampp/code/trunk/apache",
            "php": "https://svn.code.sf.net/p/xampp/code/trunk/php",
            "mysql": "https://svn.code.sf.net/p/xampp/code/trunk/mysql",
            "control": "https://svn.code.sf.net/p/xampp/code/trunk/xampp-control-panel",
        }

    def setup_logging(self):
        """Setup comprehensive logging."""
        log_file = (
            self.logs_dir / f"xampp_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def check_svn_installation(self) -> tuple[bool, str]:
        """
        Check if SVN (Subversion) is installed and available.

        Returns:
            Tuple of (is_installed, version_info)
        """
        try:
            result = subprocess.run(
                ["svn", "--version"], capture_output=True, text=True, check=True
            )

            version_info = result.stdout.strip().split("\n")[0]
            self.logger.info(f"SVN installed: {version_info}")
            return True, version_info

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.warning(f"SVN not found: {e}")
            return False, str(e)

    def install_svn_guide(self) -> dict[str, str]:
        """
        Generate SVN installation guidance for Windows.

        Returns:
            Dictionary with installation options and commands
        """
        installation_options = {
            "tortoise_svn": {
                "name": "TortoiseSVN (Recommended)",
                "url": "https://tortoisesvn.net/downloads.html",
                "description": "GUI + Command Line tools",
                "steps": [
                    "Download TortoiseSVN for Windows x64",
                    "Run installer with administrator privileges",
                    "IMPORTANT: Check 'command line client tools' during installation",
                    "Complete installation and restart computer",
                    "Verify with: svn --version",
                ],
            },
            "slik_svn": {
                "name": "SlikSVN (Command Line Only)",
                "url": "https://sliksvn.com/download/",
                "description": "Lightweight command line client",
                "steps": [
                    "Download SlikSVN for Windows x64",
                    "Run installer with default settings",
                    "Restart PowerShell/Command Prompt",
                    "Verify with: svn --version",
                ],
            },
            "chocolatey": {
                "name": "Chocolatey Package Manager",
                "command": "choco install tortoisesvn",
                "description": "Automated installation via package manager",
                "steps": [
                    "Open PowerShell as Administrator",
                    "Run: choco install tortoisesvn",
                    "Restart PowerShell",
                    "Verify with: svn --version",
                ],
            },
        }

        self.logger.info("Generated SVN installation guide")
        return installation_options

    def checkout_xampp_source(
        self, component: str = "trunk", target_dir: str | None = None
    ) -> bool:
        """
        Checkout XAMPP source code from SVN repository.

        Args:
            component: Component to checkout ('trunk', 'apache', 'php', etc.)
            target_dir: Target directory (default: xampp-dev/component-name)

        Returns:
            Success status
        """
        # Check SVN availability
        svn_available, _version_info = self.check_svn_installation()
        if not svn_available:
            self.logger.error("SVN not available. Please install SVN first.")
            return False

        # Determine source URL
        if component in self.component_urls:
            source_url = self.component_urls[component]
        elif component in self.xampp_svn_urls:
            source_url = self.xampp_svn_urls[component]
        else:
            source_url = self.xampp_svn_urls["trunk"]

        # Determine target directory
        if target_dir is None:
            target_dir = self.xampp_dev_dir / f"xampp-{component}"
        else:
            target_dir = Path(target_dir)

        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.logger.info(f"Checking out XAMPP {component} from {source_url}")
            self.logger.info(f"Target directory: {target_dir}")

            # Perform SVN checkout
            result = subprocess.run(
                ["svn", "checkout", source_url, str(target_dir)],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.xampp_dev_dir),
            )

            self.logger.info(f"Successfully checked out XAMPP {component}")
            self.logger.info(f"SVN output: {result.stdout}")

            # Log checkout information
            self.log_checkout_info(component, source_url, target_dir, result.stdout)

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"SVN checkout failed: {e}")
            self.logger.error(f"SVN stderr: {e.stderr}")
            return False

    def log_checkout_info(self, component: str, source_url: str, target_dir: Path, svn_output: str):
        """Log detailed checkout information."""
        checkout_info = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "source_url": source_url,
            "target_directory": str(target_dir),
            "svn_output": svn_output,
            "file_count": self.count_files_in_directory(target_dir),
        }

        log_file = (
            self.logs_dir
            / f"xampp_checkout_{component}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(log_file, "w") as f:
            json.dump(checkout_info, f, indent=2)

        self.logger.info(f"Checkout info logged to: {log_file}")

    def count_files_in_directory(self, directory: Path) -> int:
        """Count total files in directory recursively."""
        try:
            return sum(1 for _ in directory.rglob("*") if _.is_file())
        except Exception as e:
            self.logger.warning(f"Could not count files in {directory}: {e}")
            return 0

    def update_xampp_source(self, component: str = "trunk") -> bool:
        """
        Update existing XAMPP source code checkout.

        Args:
            component: Component to update

        Returns:
            Success status
        """
        target_dir = self.xampp_dev_dir / f"xampp-{component}"

        if not target_dir.exists():
            self.logger.error(f"No existing checkout found at {target_dir}")
            return False

        try:
            self.logger.info(f"Updating XAMPP {component} source code")

            result = subprocess.run(
                ["svn", "update"], capture_output=True, text=True, check=True, cwd=str(target_dir)
            )

            self.logger.info(f"Successfully updated XAMPP {component}")
            self.logger.info(f"Update output: {result.stdout}")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"SVN update failed: {e}")
            return False

    def analyze_xampp_structure(self, component: str = "trunk") -> dict[str, any]:
        """
        Analyze the structure of checked out XAMPP source code.

        Args:
            component: Component to analyze

        Returns:
            Analysis results dictionary
        """
        target_dir = self.xampp_dev_dir / f"xampp-{component}"

        if not target_dir.exists():
            self.logger.error(f"No checkout found at {target_dir}")
            return {}

        analysis = {
            "component": component,
            "analysis_time": datetime.now().isoformat(),
            "root_directory": str(target_dir),
            "total_files": 0,
            "total_size_mb": 0,
            "directory_structure": {},
            "file_types": {},
            "key_files": [],
        }

        try:
            # Count files and calculate size
            total_size = 0
            file_count = 0

            for file_path in target_dir.rglob("*"):
                if file_path.is_file():
                    file_count += 1
                    file_size = file_path.stat().st_size
                    total_size += file_size

                    # Track file extensions
                    suffix = file_path.suffix.lower()
                    if suffix in analysis["file_types"]:
                        analysis["file_types"][suffix] += 1
                    else:
                        analysis["file_types"][suffix] = 1

                    # Identify key files
                    if file_path.name.lower() in [
                        "readme",
                        "readme.txt",
                        "readme.md",
                        "license",
                        "changelog",
                        "makefile",
                        "configure",
                    ]:
                        analysis["key_files"].append(str(file_path.relative_to(target_dir)))

            analysis["total_files"] = file_count
            analysis["total_size_mb"] = round(total_size / (1024 * 1024), 2)

            # Analyze directory structure (top level)
            for item in target_dir.iterdir():
                if item.is_dir():
                    subdir_files = sum(1 for _ in item.rglob("*") if _.is_file())
                    analysis["directory_structure"][item.name] = subdir_files

            self.logger.info(
                f"Analyzed XAMPP {component}: {file_count} files, {analysis['total_size_mb']} MB"
            )

            # Save analysis
            analysis_file = (
                self.logs_dir
                / f"xampp_analysis_{component}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(analysis_file, "w") as f:
                json.dump(analysis, f, indent=2)

            return analysis

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return analysis

    def create_eq12_xampp_config(self) -> bool:
        """
        Create EQ12-specific XAMPP configuration for betting platform integration.

        Returns:
            Success status
        """
        try:
            # Create custom configuration directory
            eq12_config_dir = self.xampp_custom_dir / "eq12-config"
            eq12_config_dir.mkdir(exist_ok=True)

            # PHP configuration for betting platform
            php_config = {
                "php_extensions": [
                    "curl",  # For API calls
                    "json",  # JSON processing
                    "mysqli",  # Database connectivity
                    "pdo_mysql",  # PDO MySQL driver
                    "openssl",  # Security
                    "bcmath",  # Precision math for betting calculations
                    "gd",  # Image processing for charts
                    "zip",  # Archive handling
                    "xml",  # XML processing
                ],
                "php_settings": {
                    "memory_limit": "512M",
                    "max_execution_time": "300",
                    "upload_max_filesize": "100M",
                    "post_max_size": "100M",
                    "date.timezone": "UTC",
                    "log_errors": "On",
                    "display_errors": "Off",
                    "error_log": "C:/EQ12/logs/php_errors.log",
                },
            }

            # Apache configuration
            apache_config = {
                "virtual_hosts": [
                    {
                        "name": "eq12-betting.local",
                        "document_root": "C:/EQ12/dashboard",
                        "directory_index": "index.php index.html",
                        "error_log": "C:/EQ12/logs/apache_eq12_error.log",
                        "access_log": "C:/EQ12/logs/apache_eq12_access.log",
                    },
                    {
                        "name": "eq12-api.local",
                        "document_root": "C:/EQ12/api",
                        "directory_index": "index.php",
                        "error_log": "C:/EQ12/logs/apache_api_error.log",
                        "access_log": "C:/EQ12/logs/apache_api_access.log",
                    },
                ],
                "modules": [
                    "mod_rewrite",  # URL rewriting
                    "mod_ssl",  # SSL support
                    "mod_headers",  # Header manipulation
                    "mod_expires",  # Expiration headers
                    "mod_deflate",  # Compression
                ],
            }

            # MySQL configuration
            mysql_config = {
                "databases": ["eq12_betting", "eq12_analytics", "eq12_users"],
                "settings": {
                    "innodb_buffer_pool_size": "256M",
                    "max_connections": "100",
                    "query_cache_size": "64M",
                    "tmp_table_size": "64M",
                    "max_heap_table_size": "64M",
                },
            }

            # EQ12 integration configuration
            eq12_integration = {
                "python_bridge": {
                    "enabled": True,
                    "script_path": "C:/EQ12/eq12_enhanced_openai_sdk.py",
                    "api_endpoint": "http://localhost:8000/ai-analysis",
                },
                "nodejs_bridge": {
                    "enabled": True,
                    "script_path": "C:/EQ12/eq12_node_betting_suite.js",
                    "api_endpoint": "http://localhost:3000/real-time-odds",
                },
                "api_keys": {
                    "odds_api": "${ODDS_API_KEY}",
                    "openai_api": "${OPENAI_API_KEY}",
                    "telegram_bot": "${TELEGRAM_BOT_TOKEN}",
                },
            }

            # Save configurations
            configs = {
                "php": php_config,
                "apache": apache_config,
                "mysql": mysql_config,
                "eq12_integration": eq12_integration,
            }

            for config_name, config_data in configs.items():
                config_file = eq12_config_dir / f"{config_name}_config.json"
                with open(config_file, "w") as f:
                    json.dump(config_data, f, indent=2)

                self.logger.info(f"Created {config_name} configuration: {config_file}")

            # Create deployment script
            self.create_deployment_script(eq12_config_dir)

            return True

        except Exception as e:
            self.logger.error(f"Failed to create EQ12 XAMPP config: {e}")
            return False

    def create_deployment_script(self, config_dir: Path):
        """Create PowerShell deployment script for EQ12 XAMPP configuration."""

        deployment_script = """# EQ12 XAMPP Deployment Script
# Deploys EQ12-specific XAMPP configuration for betting platform

param(
    [Parameter(Mandatory=$false)]
    [string]$XamppPath = "C:\\xampp",

    [Parameter(Mandatory=$false)]
    [string]$EQ12Root = "C:\\EQ12",

    [switch]$Backup
)

Write-Host "🚀 EQ12 XAMPP Deployment Starting..." -ForegroundColor Green

# Backup existing configuration if requested
if ($Backup) {
    $BackupDir = "$EQ12Root\\logs\\xampp_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -Path $BackupDir -ItemType Directory -Force

    Write-Host "📦 Backing up existing XAMPP configuration..." -ForegroundColor Yellow

    # Backup key files
    $FilesToBackup = @(
        "$XamppPath\\php\\php.ini",
        "$XamppPath\\apache\\conf\\httpd.conf",
        "$XamppPath\\apache\\conf\\extra\\httpd-vhosts.conf",
        "$XamppPath\\mysql\\bin\\my.ini"
    )

    foreach ($File in $FilesToBackup) {
        if (Test-Path $File) {
            $BackupFile = Join-Path $BackupDir (Split-Path $File -Leaf)
            Copy-Item $File $BackupFile
            Write-Host "✅ Backed up: $(Split-Path $File -Leaf)" -ForegroundColor Gray
        }
    }
}

# Deploy EQ12 configurations
Write-Host "⚙️ Deploying EQ12 XAMPP configurations..." -ForegroundColor Cyan

# PHP Configuration
$PhpIni = "$XamppPath\\php\\php.ini"
if (Test-Path $PhpIni) {
    Write-Host "🐘 Updating PHP configuration..." -ForegroundColor Blue

    # Add EQ12-specific PHP settings
    $EQ12PhpSettings = @"

; EQ12 Betting Platform Configuration
memory_limit = 512M
max_execution_time = 300
upload_max_filesize = 100M
post_max_size = 100M
date.timezone = UTC
log_errors = On
display_errors = Off
error_log = C:/EQ12/logs/php_errors.log

; EQ12 Required Extensions
extension=curl
extension=json
extension=mysqli
extension=pdo_mysql
extension=openssl
extension=bcmath
extension=gd
extension=zip
extension=xml
"@

    Add-Content -Path $PhpIni -Value $EQ12PhpSettings
    Write-Host "✅ PHP configuration updated" -ForegroundColor Green
}

# Apache Virtual Hosts
$VhostsConf = "$XamppPath\\apache\\conf\\extra\\httpd-vhosts.conf"
if (Test-Path $VhostsConf) {
    Write-Host "🌐 Adding EQ12 virtual hosts..." -ForegroundColor Blue

    $EQ12VirtualHosts = @"

# EQ12 Betting Platform Virtual Hosts
<VirtualHost *:80>
    ServerName eq12-betting.local
    DocumentRoot "C:/EQ12/dashboard"
    DirectoryIndex index.php index.html
    ErrorLog "C:/EQ12/logs/apache_eq12_error.log"
    CustomLog "C:/EQ12/logs/apache_eq12_access.log" common

    <Directory "C:/EQ12/dashboard">
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>

<VirtualHost *:80>
    ServerName eq12-api.local
    DocumentRoot "C:/EQ12/api"
    DirectoryIndex index.php
    ErrorLog "C:/EQ12/logs/apache_api_error.log"
    CustomLog "C:/EQ12/logs/apache_api_access.log" common

    <Directory "C:/EQ12/api">
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
"@

    Add-Content -Path $VhostsConf -Value $EQ12VirtualHosts
    Write-Host "✅ Virtual hosts configured" -ForegroundColor Green
}

# Update hosts file
Write-Host "🌍 Updating Windows hosts file..." -ForegroundColor Blue
$HostsFile = "$env:SystemRoot\\System32\\drivers\\etc\\hosts"

$EQ12Hosts = @"

# EQ12 Betting Platform Local Hosts
127.0.0.1    eq12-betting.local
127.0.0.1    eq12-api.local
"@

# Check if EQ12 hosts already exist
$HostsContent = Get-Content $HostsFile -Raw
if ($HostsContent -notmatch "eq12-betting.local") {
    Add-Content -Path $HostsFile -Value $EQ12Hosts
    Write-Host "✅ Hosts file updated" -ForegroundColor Green
} else {
    Write-Host "ℹ️ EQ12 hosts already configured" -ForegroundColor Gray
}

Write-Host "🎉 EQ12 XAMPP Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Restart XAMPP services (Apache, MySQL)" -ForegroundColor White
Write-Host "2. Access EQ12 Betting Platform: http://eq12-betting.local" -ForegroundColor White
Write-Host "3. Access EQ12 API: http://eq12-api.local" -ForegroundColor White
Write-Host "4. Run EQ12 platform integration tests" -ForegroundColor White
"""

        script_file = config_dir / "Deploy-EQ12-XAMPP.ps1"
        with open(script_file, "w") as f:
            f.write(deployment_script)

        self.logger.info(f"Created deployment script: {script_file}")

    def generate_status_report(self) -> dict[str, any]:
        """Generate comprehensive status report for XAMPP integration."""

        # Check SVN status
        svn_available, svn_version = self.check_svn_installation()

        # Check existing checkouts
        checkouts = []
        if self.xampp_dev_dir.exists():
            for item in self.xampp_dev_dir.iterdir():
                if item.is_dir() and (item / ".svn").exists():
                    checkouts.append(
                        {
                            "name": item.name,
                            "path": str(item),
                            "last_modified": datetime.fromtimestamp(
                                item.stat().st_mtime
                            ).isoformat(),
                        }
                    )

        # Integration status
        integration_files = [
            "eq12_enhanced_openai_sdk.py",
            "eq12_php_odds_client.php",
            "eq12_node_odds_client.js",
            "eq12_php_betting_suite.php",
        ]

        platform_status = {}
        for file_name in integration_files:
            file_path = self.eq12_root / file_name
            platform_status[file_name] = {
                "exists": file_path.exists(),
                "size_kb": round(file_path.stat().st_size / 1024, 2) if file_path.exists() else 0,
                "last_modified": (
                    datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    if file_path.exists()
                    else None
                ),
            }

        status_report = {
            "report_time": datetime.now().isoformat(),
            "eq12_root": str(self.eq12_root),
            "xampp_integration": {
                "svn_available": svn_available,
                "svn_version": svn_version if svn_available else None,
                "xampp_dev_dir": str(self.xampp_dev_dir),
                "xampp_custom_dir": str(self.xampp_custom_dir),
                "active_checkouts": checkouts,
            },
            "platform_status": platform_status,
            "directory_structure": {
                "logs_dir": self.logs_dir.exists(),
                "configs_dir": self.configs_dir.exists(),
                "xampp_dev_dir": self.xampp_dev_dir.exists(),
                "xampp_custom_dir": self.xampp_custom_dir.exists(),
            },
        }

        # Save status report
        report_file = (
            self.logs_dir / f"xampp_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(status_report, f, indent=2)

        self.logger.info(f"Status report generated: {report_file}")
        return status_report


def main():
    """Main execution function with comprehensive CLI interface."""

    parser = argparse.ArgumentParser(
        description="EQ12 XAMPP Source Code Integration Manager",
        epilog="Integrates XAMPP source code with EQ12 tri-language betting platform",
    )

    parser.add_argument(
        "--eq12-root", default="C:\\EQ12", help="EQ12 root directory (default: C:\\EQ12)"
    )

    parser.add_argument("--check-svn", action="store_true", help="Check SVN installation status")

    parser.add_argument(
        "--install-guide", action="store_true", help="Display SVN installation guide"
    )

    parser.add_argument(
        "--checkout",
        choices=["trunk", "apache", "php", "mysql", "control"],
        help="Checkout XAMPP component source code",
    )

    parser.add_argument(
        "--update",
        choices=["trunk", "apache", "php", "mysql", "control"],
        help="Update existing XAMPP source checkout",
    )

    parser.add_argument(
        "--analyze",
        choices=["trunk", "apache", "php", "mysql", "control"],
        help="Analyze XAMPP source code structure",
    )

    parser.add_argument(
        "--create-config", action="store_true", help="Create EQ12-specific XAMPP configuration"
    )

    parser.add_argument(
        "--status-report", action="store_true", help="Generate comprehensive status report"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Adjust logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize manager
    manager = EQ12XAMPPIntegrationManager(args.eq12_root)

    try:
        # Execute requested operations
        if args.check_svn:
            svn_available, version_info = manager.check_svn_installation()
            print(f"SVN Available: {svn_available}")
            if svn_available:
                print(f"Version: {version_info}")
            else:
                print("SVN not installed. Use --install-guide for installation instructions.")

        elif args.install_guide:
            guide = manager.install_svn_guide()
            print("\n🛠️ SVN Installation Guide for Windows\n")

            for _option_key, option_info in guide.items():
                print(f"📦 {option_info['name']}")
                print(f"   Description: {option_info['description']}")
                if "url" in option_info:
                    print(f"   Download: {option_info['url']}")
                if "command" in option_info:
                    print(f"   Command: {option_info['command']}")
                print("   Steps:")
                for i, step in enumerate(option_info["steps"], 1):
                    print(f"     {i}. {step}")
                print()

        elif args.checkout:
            success = manager.checkout_xampp_source(args.checkout)
            if success:
                print(f"✅ Successfully checked out XAMPP {args.checkout}")
            else:
                print(f"❌ Failed to checkout XAMPP {args.checkout}")

        elif args.update:
            success = manager.update_xampp_source(args.update)
            if success:
                print(f"✅ Successfully updated XAMPP {args.update}")
            else:
                print(f"❌ Failed to update XAMPP {args.update}")

        elif args.analyze:
            analysis = manager.analyze_xampp_structure(args.analyze)
            if analysis:
                print(f"\n📊 XAMPP {args.analyze} Analysis Results")
                print(f"Total Files: {analysis.get('total_files', 0):,}")
                print(f"Total Size: {analysis.get('total_size_mb', 0)} MB")
                print(f"Key Directories: {len(analysis.get('directory_structure', {}))}")
                print(f"File Types: {len(analysis.get('file_types', {}))}")

        elif args.create_config:
            success = manager.create_eq12_xampp_config()
            if success:
                print("✅ Created EQ12 XAMPP configuration")
            else:
                print("❌ Failed to create EQ12 configuration")

        elif args.status_report:
            report = manager.generate_status_report()
            print("\n📋 EQ12 XAMPP Integration Status Report")
            print(f"Report Time: {report['report_time']}")
            print(f"EQ12 Root: {report['eq12_root']}")

            xampp_info = report["xampp_integration"]
            print(f"SVN Available: {xampp_info['svn_available']}")
            if xampp_info["svn_version"]:
                print(f"SVN Version: {xampp_info['svn_version']}")
            print(f"Active Checkouts: {len(xampp_info['active_checkouts'])}")

            platform_info = report["platform_status"]
            for file_name, file_info in platform_info.items():
                status = "✅" if file_info["exists"] else "❌"
                print(f"{status} {file_name}: {file_info['size_kb']} KB")

        else:
            # Default: Show status and help
            manager.generate_status_report()
            parser.print_help()

    except Exception as e:
        manager.logger.error(f"Execution failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
