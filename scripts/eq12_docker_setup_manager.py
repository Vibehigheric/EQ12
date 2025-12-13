#!/usr/bin/env python3
"""
EQ12 Docker Setup and Management System
Comprehensive Docker installation, configuration, and troubleshooting for EQ12 development
"""

import json
import logging
import os
import platform
import subprocess
import sys
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/docker_setup_manager.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EQ12DockerManager:
    """
    Comprehensive Docker management for EQ12 development environment
    Handles installation, configuration, troubleshooting, and optimization
    """

    def __init__(self):
        """Initialize EQ12 Docker Manager"""

        self.system_info = {
            "os": platform.system(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "windows_version": None,
        }

        # Get Windows version if on Windows
        if self.system_info["os"] == "Windows":
            try:
                import winreg

                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                ) as key:
                    self.system_info["windows_version"] = winreg.QueryValueEx(
                        key, "DisplayVersion"
                    )[0]
            except Exception:
                self.system_info["windows_version"] = "Unknown"

        # Docker configuration paths and URLs
        self.docker_config = {
            "desktop_download_url": "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe",
            "desktop_install_path": "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe",
            "cli_install_path": "C:\\Program Files\\Docker\\Docker\\resources\\bin\\\\docker.exe",
            "daemon_socket_windows": "npipe:////./pipe/docker_engine",
            "daemon_socket_wsl": "unix:///var/run/docker.sock",
            "config_directory": os.path.expanduser("~/.docker"),
            "eq12_compose_path": "C:/EQ12/docker-compose.yml",
        }

        # EQ12-specific Docker services
        self.eq12_services = {
            "eq12-core": {
                "description": "EQ12 Core Sports Betting Intelligence Platform",
                "image": "python:3.12-slim",
                "ports": ["8000:8000"],
                "volumes": ["C:/EQ12:/app"],
                "environment": ["PYTHONPATH=/app", "EQ12_ENV=development"],
            },
            "eq12-weather": {
                "description": "EQ12 Weather Intelligence Service",
                "image": "python:3.12-slim",
                "ports": ["8001:8001"],
                "volumes": ["C:/EQ12/scripts:/app/scripts", "C:/EQ12/logs:/app/logs"],
                "environment": ["OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}"],
            },
            "eq12-database": {
                "description": "EQ12 Sports Data Database",
                "image": "postgres:15-alpine",
                "ports": ["5432:5432"],
                "volumes": ["eq12-postgres-data:/var/lib/postgresql/data"],
                "environment": [
                    "POSTGRES_DB=eq12_sports",
                    "POSTGRES_USER=eq12",
                    "POSTGRES_PASSWORD=${DB_PASSWORD}",
                ],
            },
            "eq12-redis": {
                "description": "EQ12 Cache and Session Store",
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
                "volumes": ["eq12-redis-data:/data"],
            },
            "eq12-dashboard": {
                "description": "EQ12 Web Dashboard",
                "image": "nginx:alpine",
                "ports": ["80:80", "443:443"],
                "volumes": ["C:/EQ12/dashboard:/usr/share/nginx/html"],
            },
        }

        logger.info("EQ12 Docker Manager initialized")
        logger.info(
            f"System: {
                self.system_info['os']} {
                self.system_info['architecture']} - {
                self.system_info['windows_version']}")

    def check_docker_status(self) -> dict[str, Any]:
        """Comprehensive Docker installation and status check"""

        logger.info("Checking Docker installation and status...")

        status = {
            "docker_installed": False,
            "docker_desktop_installed": False,
            "docker_running": False,
            "docker_version": None,
            "docker_compose_available": False,
            "wsl2_available": False,
            "hyper_v_enabled": False,
            "issues": [],
            "recommendations": [],
        }

        # Check Docker Desktop installation
        if os.path.exists(self.docker_config["desktop_install_path"]):
            status["docker_desktop_installed"] = True
            logger.info("Docker Desktop installation found")
        else:
            status["issues"].append("Docker Desktop not installed")
            status["recommendations"].append("Install Docker Desktop for Windows")

        # Check Docker CLI availability
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                status["docker_installed"] = True
                status["docker_version"] = result.stdout.strip()
                logger.info(f"Docker CLI available: {status['docker_version']}")
            else:
                status["issues"].append("Docker CLI not accessible")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            status["issues"].append(f"Docker CLI check failed: {e!s}")

        # Check Docker daemon status
        try:
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                status["docker_running"] = True
                logger.info("Docker daemon is running")

                # Parse docker info for additional details
                docker_info = result.stdout.lower()
                if "server version:" in docker_info:
                    for line in docker_info.split("\n"):
                        if "server version:" in line:
                            status["docker_version"] = line.strip()
                            break

            else:
                status["issues"].append("Docker daemon not running")
                status["recommendations"].append("Start Docker Desktop")

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            status["issues"].append(f"Docker daemon check failed: {e!s}")

        # Check Docker Compose availability
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                status["docker_compose_available"] = True
                logger.info("Docker Compose available")
            else:
                status["issues"].append("Docker Compose not available")
        except Exception as e:
            status["issues"].append(f"Docker Compose check failed: {e!s}")

        # Check WSL2 availability (Windows only)
        if self.system_info["os"] == "Windows":
            try:
                result = subprocess.run(
                    ["wsl", "--list", "--verbose"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and "VERSION 2" in result.stdout:
                    status["wsl2_available"] = True
                    logger.info("WSL2 available")
                else:
                    status["issues"].append("WSL2 not properly configured")
                    status["recommendations"].append(
                        "Enable WSL2 for better Docker performance")
            except Exception as e:
                status["issues"].append(f"WSL2 check failed: {e!s}")

        # Check Hyper-V (Windows Pro/Enterprise)
        if self.system_info["os"] == "Windows":
            try:
                result = subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and "Enabled" in result.stdout:
                    status["hyper_v_enabled"] = True
                    logger.info("Hyper-V is enabled")
            except Exception as e:
                logger.warning(f"Hyper-V check failed: {e}")

        return status

    def generate_docker_installation_guide(self) -> dict[str, Any]:
        """Generate comprehensive Docker installation guide for EQ12 system"""

        guide = {"system_requirements": {"windows_version": "Windows 10/11 Pro, Enterprise, or Education (64-bit)",
                                         "memory": "Minimum 4GB RAM (8GB+ recommended)",
                                         "storage": "Minimum 20GB available disk space",
                                         "virtualization": "Hardware virtualization support (Intel VT-x or AMD-V)",
                                         "wsl2": "Windows Subsystem for Linux 2 (recommended)",
                                         "hyper_v": "Hyper-V (alternative to WSL2)",
                                         },
                 "installation_steps": [{"step": 1,
                                         "title": "Download Docker Desktop",
                                         "description": "Download Docker Desktop for Windows from official website",
                                         "action": f'Visit {self.docker_config["desktop_download_url"]} or use winget',
                                         "command": "winget install Docker.DockerDesktop",
                                         "verification": "File downloaded to Downloads folder",
                                         },
                                        {"step": 2,
                                         "title": "Run Docker Desktop Installer",
                                         "description": "Execute installer with administrator privileges",
                                         "action": "Right-click installer → Run as administrator",
                                         "command": None,
                                         "verification": "Installation wizard appears",
                                         },
                                        {"step": 3,
                                         "title": "Configure Installation Options",
                                         "description": "Select WSL2 backend (recommended) or Hyper-V",
                                         "action": 'Check "Use WSL 2 instead of Hyper-V" option',
                                         "command": None,
                                         "verification": "Installation options configured",
                                         },
                                        {"step": 4,
                                         "title": "Complete Installation",
                                         "description": "Wait for installation to complete and restart system",
                                         "action": 'Click "Close and log out" when prompted',
                                         "command": None,
                                         "verification": "System restart completed",
                                         },
                                        {"step": 5,
                                         "title": "Start Docker Desktop",
                                         "description": "Launch Docker Desktop and complete initial setup",
                                         "action": "Start Menu → Docker Desktop",
                                         "command": None,
                                         "verification": "Docker Desktop GUI opens successfully",
                                         },
                                        {"step": 6,
                                         "title": "Verify Installation",
                                         "description": "Test Docker functionality from command line",
                                         "action": "Open PowerShell and run docker commands",
                                         "command": "docker --version && docker run hello-world",
                                         "verification": "Docker version displayed and hello-world container runs",
                                         },
                                        ],
                 "troubleshooting_steps": [{"issue": "WSL2 not installed or configured",
                                            "solution": "Enable WSL2 feature and install Linux distribution",
                                            "commands": ["dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart",
                                                         "dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart",
                                                         "wsl --set-default-version 2",
                                                         "wsl --install -d Ubuntu",
                                                         ],
                                            },
                                           {"issue": "Hyper-V conflicts or not available",
                                            "solution": "Enable Hyper-V or switch to WSL2 backend",
                                            "commands": ["Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All"],
                                            },
                                           {"issue": "Docker daemon not starting",
                                            "solution": "Check system resources and restart Docker Desktop",
                                            "commands": ['Get-Process -Name "*Docker*" | Stop-Process -Force',
                                                         'Start-Process "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"',
                                                         ],
                                            },
                                           {"issue": "Permission denied errors",
                                            "solution": "Add user to docker-users group",
                                            "commands": ['net localgroup docker-users "your-username" /add'],
                                            },
                                           ],
                 "eq12_optimization": {"docker_desktop_settings": {"memory": "8GB (or 50% of total RAM)",
                                                                   "cpu": "4 cores (or 50% of total cores)",
                                                                   "disk_size": "100GB for EQ12 containers and images",
                                                                   "swap": "2GB",
                                                                   "file_sharing": ["C:\\\\EQ12"],
                                                                   "wsl_integration": True,
                                                                   },
                                       "performance_recommendations": ["Enable WSL2 backend for better performance",
                                                                       "Allocate sufficient memory for EQ12 services",
                                                                       "Use bind mounts for EQ12 code directories",
                                                                       "Configure Docker to start with Windows",
                                                                       "Enable BuildKit for faster image builds",
                                                                       ],
                                       },
                 }

        return guide

    def create_eq12_docker_compose(self) -> str:
        """Create optimized Docker Compose configuration for EQ12 system"""

        compose_config = {
            "version": "3.8",
            "services": {},
            "volumes": {
                "eq12-postgres-data": {"driver": "local"},
                "eq12-redis-data": {"driver": "local"},
            },
            "networks": {
                "eq12-network": {
                    "driver": "bridge",
                    "ipam": {"config": [{"subnet": "172.20.0.0/16"}]},
                }
            },
        }

        # Generate service configurations
        for service_name, service_config in self.eq12_services.items():

            compose_service = {
                "image": service_config["image"],
                "container_name": f'eq12-{service_name.replace("eq12-", "")}',
                "restart": "unless-stopped",
                "networks": ["eq12-network"],
            }

            # Add ports if specified
            if "ports" in service_config:
                compose_service["ports"] = service_config["ports"]

            # Add volumes if specified
            if "volumes" in service_config:
                compose_service["volumes"] = service_config["volumes"]

            # Add environment variables if specified
            if "environment" in service_config:
                compose_service["environment"] = service_config["environment"]

            # Service-specific configurations
            if service_name == "eq12-core":
                compose_service.update(
                    {
                        "working_dir": "/app",
                        "command": "python -m http.server 8000",
                        "depends_on": ["eq12-database", "eq12-redis"],
                        "healthcheck": {
                            "test": ["CMD", "curl", "-", "http://localhost:8000"],
                            "interval": "30s",
                            "timeout": "10s",
                            "retries": 3,
                        },
                    }
                )

            elif service_name == "eq12-weather":
                compose_service.update(
                    {
                        "working_dir": "/app/scripts",
                        "command": "python -m http.server 8001",
                        "depends_on": ["eq12-redis"],
                    }
                )

            elif service_name == "eq12-database":
                compose_service.update(
                    {
                        "healthcheck": {
                            "test": ["CMD-SHELL", "pg_isready -U eq12"],
                            "interval": "10s",
                            "timeout": "5s",
                            "retries": 5,
                        }
                    }
                )

            elif service_name == "eq12-redis":
                compose_service.update(
                    {
                        "command": "redis-server --appendonly yes",
                        "healthcheck": {
                            "test": ["CMD", "redis-cli", "ping"],
                            "interval": "10s",
                            "timeout": "3s",
                            "retries": 3,
                        },
                    }
                )

            elif service_name == "eq12-dashboard":
                compose_service.update({"depends_on": ["eq12-core", "eq12-weather"]})

            compose_config["services"][service_name] = compose_service

        # Convert to YAML format
        import yaml

        compose_yaml = yaml.dump(
            compose_config,
            default_flow_style=False,
            sort_keys=False)

        # Save Docker Compose file
        compose_file_path = self.docker_config["eq12_compose_path"]

        with open(compose_file_path, "w", encoding="utf-8") as f:
            f.write(compose_yaml)

        logger.info(f"EQ12 Docker Compose configuration saved: {compose_file_path}")
        return compose_file_path

    def create_dockerfiles(self) -> dict[str, str]:
        """Create optimized Dockerfiles for EQ12 services"""

        # EQ12 Core Application Dockerfile
        eq12_core_dockerfile = """# EQ12 Core Sports Betting Intelligence Platform
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

        # EQ12 Weather Service Dockerfile
        eq12_weather_dockerfile = """# EQ12 Weather Intelligence Service
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy weather service requirements
COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts
COPY scripts/ ./scripts/
COPY logs/ ./logs/

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=60s --timeout=15s --start-period=10s --retries=3 \\
    CMD python scripts/health_check.py || exit 1

# Start weather service
CMD ["python", "scripts/eq12_weather_service.py", "--port", "8001"]
"""

        # Save Dockerfiles
        dockerfiles_created = {}

        # Core application Dockerfile
        core_dockerfile_path = "C:/EQ12/Dockerfile"
        with open(core_dockerfile_path, "w", encoding="utf-8") as f:
            f.write(eq12_core_dockerfile)
        dockerfiles_created["core"] = core_dockerfile_path

        # Weather service Dockerfile
        weather_dockerfile_path = "C:/EQ12/Dockerfile.weather"
        with open(weather_dockerfile_path, "w", encoding="utf-8") as f:
            f.write(eq12_weather_dockerfile)
        dockerfiles_created["weather"] = weather_dockerfile_path

        logger.info(f"Created {len(dockerfiles_created)} Dockerfiles for EQ12 services")
        return dockerfiles_created

    def generate_docker_commands(self) -> dict[str, list[str]]:
        """Generate essential Docker commands for EQ12 development"""

        commands = {
            "installation_verification": [
                "docker --version",
                "docker info",
                "docker compose version",
                "docker run hello-world",
            ],
            "eq12_development": [
                "cd C:\\\\EQ12",
                "docker compose up -d",
                "docker compose ps",
                "docker compose logs -f eq12-core",
                "docker compose exec eq12-core python --version",
            ],
            "troubleshooting": [
                "docker system info",
                "docker system df",
                "docker ps -a",
                "docker images",
                "docker network ls",
                "docker volume ls",
            ],
            "maintenance": [
                "docker system prune -f",
                "docker image prune -f",
                "docker volume prune -f",
                "docker network prune -f",
                "docker compose down --volumes",
            ],
            "eq12_specific": [
                "docker compose build eq12-core",
                "docker compose up --build",
                "docker compose restart eq12-weather",
                "docker compose logs --tail=100 eq12-database",
                "docker exec -it eq12-core bash",
            ],
        }

        return commands

    def create_comprehensive_setup_script(self) -> str:
        """Create comprehensive Docker setup script for EQ12"""

        script_content = """# EQ12 Docker Setup and Management Script
# Comprehensive Docker installation and configuration for EQ12 system

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet("install", "setup", "start", "stop", "status", "troubleshoot", "clean")]
    [string]$Action = "status",

    [Parameter()]
    [switch]$Force,

    [Parameter()]
    [switch]$Verbose
)

$ErrorActionPreference = 'Stop'

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARNING" { Write-Host $logMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        "INFO" { Write-Host $logMessage -ForegroundColor Cyan }
        default { Write-Host $logMessage }
    }

    Add-Content -Path "C:\\\\EQ12\\logs\\\\docker_setup.log" -Value $logMessage
}

function Test-DockerInstallation {
    Write-EQ12Log "Checking Docker installation status..."

    $dockerStatus = @{
        DockerDesktopInstalled = $false
        DockerRunning = $false
        DockerVersion = $null
        ComposeAvailable = $false
        Issues = @()
    }

    # Check Docker Desktop installation
    if (Test-Path "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe") {
        $dockerStatus.DockerDesktopInstalled = $true
        Write-EQ12Log "Docker Desktop installation found" -Level "SUCCESS"
    } else {
        $dockerStatus.Issues += "Docker Desktop not installed"
        Write-EQ12Log "Docker Desktop not found" -Level "WARNING"
    }

    # Check Docker CLI
    try {
        $version = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $dockerStatus.DockerVersion = $version
            Write-EQ12Log "Docker CLI available: $version" -Level "SUCCESS"
        }
    } catch {
        $dockerStatus.Issues += "Docker CLI not accessible"
    }

    # Check Docker daemon
    try {
        docker info 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $dockerStatus.DockerRunning = $true
            Write-EQ12Log "Docker daemon is running" -Level "SUCCESS"
        }
    } catch {
        $dockerStatus.Issues += "Docker daemon not running"
    }

    # Check Docker Compose
    try {
        docker compose version 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $dockerStatus.ComposeAvailable = $true
            Write-EQ12Log "Docker Compose available" -Level "SUCCESS"
        }
    } catch {
        $dockerStatus.Issues += "Docker Compose not available"
    }

    return $dockerStatus
}

function Install-DockerDesktop {
    Write-EQ12Log "Starting Docker Desktop installation..."

    # Check if winget is available
    try {
        winget --version | Out-Null
        Write-EQ12Log "Using winget for installation"
        winget install Docker.DockerDesktop
    } catch {
        Write-EQ12Log "Winget not available, downloading manually..." -Level "WARNING"

        $downloadUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
        $installerPath = "$env:TEMP\\DockerDesktopInstaller.exe"

        Write-EQ12Log "Downloading Docker Desktop installer..."
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath

        Write-EQ12Log "Running Docker Desktop installer..."
        Start-Process -FilePath $installerPath -ArgumentList "install", "--quiet" -Wait
    }

    Write-EQ12Log "Docker Desktop installation completed" -Level "SUCCESS"
    Write-EQ12Log "Please restart your computer to complete the installation" -Level "WARNING"
}

function Start-EQ12Services {
    Write-EQ12Log "Starting EQ12 Docker services..."

    if (Test-Path "C:\\\\EQ12\\\\docker-compose.yml") {
        Set-Location "C:\\\\EQ12"

        Write-EQ12Log "Building and starting EQ12 services..."
        docker compose up -d --build

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "EQ12 services started successfully" -Level "SUCCESS"

            # Show service status
            Write-EQ12Log "Service status:"
            docker compose ps
        } else {
            Write-EQ12Log "Failed to start EQ12 services" -Level "ERROR"
        }
    } else {
        Write-EQ12Log "Docker Compose file not found. Run setup first." -Level "ERROR"
    }
}

function Stop-EQ12Services {
    Write-EQ12Log "Stopping EQ12 Docker services..."

    if (Test-Path "C:\\\\EQ12\\\\docker-compose.yml") {
        Set-Location "C:\\\\EQ12"
        docker compose down

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "EQ12 services stopped successfully" -Level "SUCCESS"
        } else {
            Write-EQ12Log "Failed to stop EQ12 services" -Level "ERROR"
        }
    }
}

function Show-DockerStatus {
    Write-EQ12Log "Docker Status Report" -Level "INFO"
    Write-Host "=" * 60

    $status = Test-DockerInstallation

    Write-Host "Docker Desktop Installed: " -NoNewline
    if ($status.DockerDesktopInstalled) {
        Write-Host "✅ YES" -ForegroundColor Green
    } else {
        Write-Host "❌ NO" -ForegroundColor Red
    }

    Write-Host "Docker Daemon Running: " -NoNewline
    if ($status.DockerRunning) {
        Write-Host "✅ YES" -ForegroundColor Green
    } else {
        Write-Host "❌ NO" -ForegroundColor Red
    }

    if ($status.DockerVersion) {
        Write-Host "Docker Version: $($status.DockerVersion)" -ForegroundColor Cyan
    }

    Write-Host "Docker Compose Available: " -NoNewline
    if ($status.ComposeAvailable) {
        Write-Host "✅ YES" -ForegroundColor Green
    } else {
        Write-Host "❌ NO" -ForegroundColor Red
    }

    if ($status.Issues.Count -gt 0) {
        Write-Host "`nIssues Found:" -ForegroundColor Yellow
        foreach ($issue in $status.Issues) {
            Write-Host "  • $issue" -ForegroundColor Red
        }
    }

    # Show EQ12 services status if Docker is running
    if ($status.DockerRunning -and (Test-Path "C:\\\\EQ12\\\\docker-compose.yml")) {
        Write-Host "`nEQ12 Services Status:" -ForegroundColor Cyan
        Set-Location "C:\\\\EQ12"
        docker compose ps
    }
}

# Main execution
Write-Host "🐋 EQ12 DOCKER SETUP AND MANAGEMENT" -ForegroundColor Cyan
Write-Host "=" * 60

switch ($Action.ToLower()) {
    "install" {
        $status = Test-DockerInstallation
        if ($status.DockerDesktopInstalled -and -not $Force) {
            Write-EQ12Log "Docker Desktop already installed. Use -Force to reinstall." -Level "WARNING"
        } else {
            Install-DockerDesktop
        }
    }

    "setup" {
        Write-EQ12Log "Setting up EQ12 Docker environment..."
        # This would call the Python script to generate compose files
        python "C:\\\\EQ12\\\\scripts\\\\eq12_docker_setup_manager.py" --setup
    }

    "start" {
        Start-EQ12Services
    }

    "stop" {
        Stop-EQ12Services
    }

    "status" {
        Show-DockerStatus
    }

    "troubleshoot" {
        Write-EQ12Log "Running Docker troubleshooting..."
        Show-DockerStatus

        Write-Host "`nTroubleshooting Information:" -ForegroundColor Yellow
        Write-Host "System Info:" -ForegroundColor Cyan
        docker system info 2>$null

        Write-Host "`nDisk Usage:" -ForegroundColor Cyan
        docker system df 2>$null

        Write-Host "`nRunning Containers:" -ForegroundColor Cyan
        docker ps 2>$null
    }

    "clean" {
        Write-EQ12Log "Cleaning Docker system..."
        docker system prune -f
        docker image prune -f
        docker volume prune -f
        Write-EQ12Log "Docker cleanup completed" -Level "SUCCESS"
    }

    default {
        Show-DockerStatus
    }
}

Write-Host "`n✅ EQ12 Docker Management Complete!" -ForegroundColor Green
"""

        # Save setup script
        script_path = "C:/EQ12/scripts/eq12_docker_setup.ps1"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        logger.info(f"EQ12 Docker setup script created: {script_path}")
        return script_path


def main():
    """Main execution function for Docker setup and management"""

    print("🐋 EQ12 DOCKER SETUP AND MANAGEMENT SYSTEM")
    print("=" * 80)
    print()

    # Initialize Docker Manager
    docker_manager = EQ12DockerManager()

    # Check current Docker status
    print("📊 CURRENT DOCKER STATUS")
    print("-" * 40)
    status = docker_manager.check_docker_status()

    print(
        f"Docker Desktop Installed: {
            '✅ YES' if status['docker_desktop_installed'] else '❌ NO'}")
    print(f"Docker CLI Available: {'✅ YES' if status['docker_installed'] else '❌ NO'}")
    print(f"Docker Daemon Running: {'✅ YES' if status['docker_running'] else '❌ NO'}")
    print(
        f"Docker Compose Available: {
            '✅ YES' if status['docker_compose_available'] else '❌ NO'}")

    if status["docker_version"]:
        print(f"Docker Version: {status['docker_version']}")

    if status["wsl2_available"]:
        print("WSL2 Backend: ✅ Available")

    print()

    # Show issues and recommendations
    if status["issues"]:
        print("⚠️ ISSUES DETECTED:")
        for issue in status["issues"]:
            print(f"   • {issue}")
        print()

    if status["recommendations"]:
        print("💡 RECOMMENDATIONS:")
        for rec in status["recommendations"]:
            print(f"   • {rec}")
        print()

    # Generate installation guide if Docker not installed
    if not status["docker_desktop_installed"]:
        print("📋 DOCKER INSTALLATION GUIDE")
        print("-" * 40)
        guide = docker_manager.generate_docker_installation_guide()

        print("SYSTEM REQUIREMENTS:")
        for req, value in guide["system_requirements"].items():
            print(f"   • {req.replace('_', ' ').title()}: {value}")
        print()

        print("INSTALLATION STEPS:")
        for step in guide["installation_steps"][:3]:  # Show first 3 steps
            print(f"   {step['step']}. {step['title']}")
            print(f"      {step['description']}")
            if step["command"]:
                print(f"      Command: {step['command']}")
            print()

        print("💻 AUTOMATED INSTALLATION:")
        print("   Run: winget install Docker.DockerDesktop")
        print("   Or: C:\\\\EQ12\\\\scripts\\\\eq12_docker_setup.ps1 -Action install")
        print()

    # Create EQ12 Docker configuration
    if status["docker_installed"] or True:  # Always create for reference
        print("🔧 GENERATING EQ12 DOCKER CONFIGURATION")
        print("-" * 40)

        # Create Docker Compose configuration
        compose_path = docker_manager.create_eq12_docker_compose()
        print(f"✅ Docker Compose created: {compose_path}")

        # Create Dockerfiles
        dockerfiles = docker_manager.create_dockerfiles()
        print(f"✅ Created {len(dockerfiles)} Dockerfiles")

        # Create setup script
        script_path = docker_manager.create_comprehensive_setup_script()
        print(f"✅ Setup script created: {script_path}")
        print()

    # Show essential commands
    print("🚀 ESSENTIAL DOCKER COMMANDS FOR EQ12")
    print("-" * 40)
    commands = docker_manager.generate_docker_commands()

    print("INSTALLATION VERIFICATION:")
    for cmd in commands["installation_verification"][:3]:
        print(f"   {cmd}")
    print()

    print("EQ12 DEVELOPMENT:")
    for cmd in commands["eq12_development"][:3]:
        print(f"   {cmd}")
    print()

    print("QUICK START:")
    print("   1. Install Docker Desktop (if not installed)")
    print("   2. cd C:\\\\EQ12")
    print("   3. docker compose up -d")
    print("   4. Open http://localhost:8000")
    print()

    # Save comprehensive status report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"C:/EQ12/logs/docker_setup_report_{timestamp}.json"

    report = {
        "timestamp": timestamp,
        "system_info": docker_manager.system_info,
        "docker_status": status,
        "installation_guide": docker_manager.generate_docker_installation_guide(),
        "essential_commands": commands,
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📋 Comprehensive Docker setup report saved: {report_file}")
    print()

    # Final recommendations
    if not status["docker_desktop_installed"]:
        print("🎯 NEXT STEPS:")
        print("   1. Install Docker Desktop: winget install Docker.DockerDesktop")
        print("   2. Restart your computer")
        print("   3. Run: C:\\\\EQ12\\\\scripts\\\\eq12_docker_setup.ps1 -Action setup")
        print("   4. Start EQ12 services: docker compose up -d")
    elif not status["docker_running"]:
        print("🎯 NEXT STEPS:")
        print("   1. Start Docker Desktop")
        print("   2. Run: C:\\\\EQ12\\\\scripts\\\\eq12_docker_setup.ps1 -Action start")
    else:
        print("✅ DOCKER IS READY!")
        print("   Your EQ12 system can now use Docker containers!")
        print("   Run 'docker compose up -d' in C:\\\\EQ12 to start services")

    print()
    print("✅ EQ12 Docker Setup and Management Complete!")


if __name__ == "__main__":
    main()
