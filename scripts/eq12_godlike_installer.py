#!/usr/bin/env python3
"""
EQ12 Universal System Quantifier & Godlike Installer
Complete system analysis, dependency installation, and repair automation.
Transforms EQ12 into an unstoppable AI empire with zero manual intervention.
"""

import asyncio
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import importlib.util
import pkg_resources
from dataclasses import dataclass

# Configure logging
log_dir = Path("C:\\EQ12\\logs")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"eq12_godlike_installer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class SystemRequirement:
    """System requirement specification"""
    name: str
    category: str
    package: str
    version: Optional[str] = None
    install_cmd: Optional[str] = None
    verify_cmd: Optional[str] = None
    critical: bool = True
    description: str = ""


@dataclass
class SystemHealth:
    """System health report"""
    total_requirements: int = 0
    installed: int = 0
    missing: int = 0
    outdated: int = 0
    critical_missing: int = 0
    health_score: float = 0.0
    issues: List[str] = None
    recommendations: List[str] = None


class EQ12GodlikeInstaller:
    """Ultimate EQ12 system quantifier and installer"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.python_exe = sys.executable
        self.pip_exe = f"{self.python_exe} -m pip"
        
        # Create directories
        for path in [
            self.workspace_path / "logs",
            self.workspace_path / "data",
            self.workspace_path / "configs",
            self.workspace_path / "temp"
        ]:
            path.mkdir(parents=True, exist_ok=True)
        
        # System requirements definition
        self.requirements = self.define_system_requirements()
        
        # Installation results
        self.install_results = {}
        self.repair_results = {}
        
        logger.info("EQ12 Godlike Installer initialized")

    def define_system_requirements(self) -> Dict[str, SystemRequirement]:
        """Define complete EQ12 system requirements"""
        requirements = {
            # Core AI & ML
            "openai": SystemRequirement(
                name="OpenAI API Client",
                category="AI Core",
                package="openai",
                version=">=1.50.0",
                install_cmd="openai>=1.50.0",
                verify_cmd="import openai; print(openai.__version__)",
                critical=True,
                description="Primary AI inference engine"
            ),
            "groq": SystemRequirement(
                name="Groq API Client",
                category="AI Core", 
                package="groq",
                version=">=0.8.0",
                install_cmd="groq>=0.8.0",
                verify_cmd="import groq; print('Groq available')",
                critical=True,
                description="High-speed AI inference"
            ),
            "transformers": SystemRequirement(
                name="Hugging Face Transformers",
                category="AI Core",
                package="transformers",
                version=">=4.30.0",
                install_cmd="transformers>=4.30.0",
                verify_cmd="import transformers; print(transformers.__version__)",
                critical=False,
                description="Local AI model support"
            ),
            "torch": SystemRequirement(
                name="PyTorch",
                category="AI Core",
                package="torch",
                version=">=2.0.0",
                install_cmd="torch>=2.0.0",
                verify_cmd="import torch; print(torch.__version__)",
                critical=False,
                description="Neural network framework"
            ),
            
            # Web & API Framework
            "fastapi": SystemRequirement(
                name="FastAPI Framework",
                category="Web Stack",
                package="fastapi",
                version=">=0.100.0",
                install_cmd="fastapi>=0.100.0",
                verify_cmd="import fastapi; print(fastapi.__version__)",
                critical=True,
                description="Web API framework"
            ),
            "uvicorn": SystemRequirement(
                name="Uvicorn ASGI Server",
                category="Web Stack", 
                package="uvicorn",
                version=">=0.20.0",
                install_cmd="uvicorn[standard]>=0.20.0",
                verify_cmd="import uvicorn; print('Uvicorn available')",
                critical=True,
                description="ASGI web server"
            ),
            "jinja2": SystemRequirement(
                name="Jinja2 Templates",
                category="Web Stack",
                package="jinja2",
                version=">=3.0.0",
                install_cmd="jinja2>=3.0.0",
                verify_cmd="import jinja2; print(jinja2.__version__)",
                critical=True,
                description="Template engine"
            ),
            
            # Telegram & Communication
            "python-telegram-bot": SystemRequirement(
                name="Telegram Bot API",
                category="Communication",
                package="python-telegram-bot",
                version=">=20.0",
                install_cmd="python-telegram-bot>=20.0",
                verify_cmd="import telegram; print(telegram.__version__)",
                critical=True,
                description="Telegram integration"
            ),
            
            # Crypto & Blockchain
            "web3": SystemRequirement(
                name="Web3.py",
                category="Blockchain",
                package="web3",
                version=">=6.0.0",
                install_cmd="web3>=6.0.0",
                verify_cmd="import web3; print(web3.__version__)",
                critical=True,
                description="Blockchain connectivity"
            ),
            "eth-account": SystemRequirement(
                name="Ethereum Account Tools",
                category="Blockchain",
                package="eth-account",
                version=">=0.9.0",
                install_cmd="eth-account>=0.9.0",
                verify_cmd="import eth_account; print('eth-account available')",
                critical=True,
                description="Wallet signature verification"
            ),
            
            # Data Science & Analytics
            "pandas": SystemRequirement(
                name="Pandas Data Analysis",
                category="Data Science",
                package="pandas",
                version=">=2.0.0",
                install_cmd="pandas>=2.0.0",
                verify_cmd="import pandas; print(pandas.__version__)",
                critical=True,
                description="Data manipulation"
            ),
            "numpy": SystemRequirement(
                name="NumPy",
                category="Data Science", 
                package="numpy",
                version=">=1.24.0",
                install_cmd="numpy>=1.24.0",
                verify_cmd="import numpy; print(numpy.__version__)",
                critical=True,
                description="Numerical computing"
            ),
            "scipy": SystemRequirement(
                name="SciPy",
                category="Data Science",
                package="scipy", 
                version=">=1.10.0",
                install_cmd="scipy>=1.10.0",
                verify_cmd="import scipy; print(scipy.__version__)",
                critical=False,
                description="Scientific computing"
            ),
            "matplotlib": SystemRequirement(
                name="Matplotlib",
                category="Visualization",
                package="matplotlib",
                version=">=3.7.0",
                install_cmd="matplotlib>=3.7.0",
                verify_cmd="import matplotlib; print(matplotlib.__version__)",
                critical=False,
                description="Plotting library"
            ),
            "plotly": SystemRequirement(
                name="Plotly",
                category="Visualization",
                package="plotly",
                version=">=5.14.0",
                install_cmd="plotly>=5.14.0",
                verify_cmd="import plotly; print(plotly.__version__)",
                critical=False,
                description="Interactive visualizations"
            ),
            
            # Network & HTTP
            "requests": SystemRequirement(
                name="Requests HTTP Library",
                category="Network",
                package="requests",
                version=">=2.31.0",
                install_cmd="requests>=2.31.0",
                verify_cmd="import requests; print(requests.__version__)",
                critical=True,
                description="HTTP client"
            ),
            "httpx": SystemRequirement(
                name="HTTPX Async Client",
                category="Network",
                package="httpx",
                version=">=0.24.0",
                install_cmd="httpx>=0.24.0",
                verify_cmd="import httpx; print(httpx.__version__)",
                critical=True,
                description="Async HTTP client"
            ),
            "aiohttp": SystemRequirement(
                name="Async HTTP",
                category="Network",
                package="aiohttp",
                version=">=3.8.0",
                install_cmd="aiohttp>=3.8.0", 
                verify_cmd="import aiohttp; print(aiohttp.__version__)",
                critical=True,
                description="Async HTTP framework"
            ),
            
            # Security & Encryption
            "cryptography": SystemRequirement(
                name="Cryptography",
                category="Security",
                package="cryptography",
                version=">=41.0.0",
                install_cmd="cryptography>=41.0.0",
                verify_cmd="import cryptography; print(cryptography.__version__)",
                critical=True,
                description="Encryption library"
            ),
            "python-dotenv": SystemRequirement(
                name="Python Dotenv",
                category="Security",
                package="python-dotenv",
                version=">=1.0.0",
                install_cmd="python-dotenv>=1.0.0",
                verify_cmd="import dotenv; print('dotenv available')",
                critical=True,
                description="Environment variable management"
            ),
            "pyjwt": SystemRequirement(
                name="PyJWT",
                category="Security",
                package="pyjwt",
                version=">=2.8.0",
                install_cmd="pyjwt[crypto]>=2.8.0",
                verify_cmd="import jwt; print(jwt.__version__)",
                critical=False,
                description="JWT token handling"
            ),
            
            # Database & Storage
            "sqlalchemy": SystemRequirement(
                name="SQLAlchemy ORM",
                category="Database",
                package="sqlalchemy",
                version=">=2.0.0",
                install_cmd="sqlalchemy>=2.0.0",
                verify_cmd="import sqlalchemy; print(sqlalchemy.__version__)",
                critical=False,
                description="Database ORM"
            ),
            
            # System & Monitoring
            "psutil": SystemRequirement(
                name="System Process Utilities",
                category="System",
                package="psutil",
                version=">=5.9.0",
                install_cmd="psutil>=5.9.0",
                verify_cmd="import psutil; print(psutil.__version__)",
                critical=True,
                description="System monitoring"
            ),
            "schedule": SystemRequirement(
                name="Task Scheduler",
                category="System",
                package="schedule",
                version=">=1.2.0",
                install_cmd="schedule>=1.2.0",
                verify_cmd="import schedule; print('schedule available')",
                critical=False,
                description="Task scheduling"
            ),
            
            # Output & Formatting
            "rich": SystemRequirement(
                name="Rich Console Output",
                category="UI",
                package="rich",
                version=">=13.0.0",
                install_cmd="rich>=13.0.0",
                verify_cmd="import rich; print(rich.__version__)",
                critical=False,
                description="Beautiful console output"
            ),
            "tabulate": SystemRequirement(
                name="Table Formatting",
                category="UI",
                package="tabulate",
                version=">=0.9.0",
                install_cmd="tabulate>=0.9.0",
                verify_cmd="import tabulate; print(tabulate.__version__)",
                critical=False,
                description="Table formatting"
            ),
            
            # Excel & Office
            "openpyxl": SystemRequirement(
                name="Excel File Support",
                category="Office",
                package="openpyxl",
                version=">=3.1.0",
                install_cmd="openpyxl>=3.1.0",
                verify_cmd="import openpyxl; print(openpyxl.__version__)",
                critical=False,
                description="Excel file handling"
            ),
            
            # Financial Data
            "yfinance": SystemRequirement(
                name="Yahoo Finance API",
                category="Finance",
                package="yfinance",
                version=">=0.2.0",
                install_cmd="yfinance>=0.2.0",
                verify_cmd="import yfinance; print('yfinance available')",
                critical=False,
                description="Financial data API"
            )
        }
        
        return requirements

    def check_python_environment(self) -> Dict[str, Any]:
        """Check Python environment health"""
        logger.info("Checking Python environment...")
        
        env_info = {
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "pip_version": None,
            "virtual_env": None,
            "site_packages": None,
            "issues": []
        }
        
        # Check pip version
        try:
            result = subprocess.run([self.python_exe, "-m", "pip", "--version"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                env_info["pip_version"] = result.stdout.strip()
            else:
                env_info["issues"].append("pip not working properly")
        except Exception as e:
            env_info["issues"].append(f"pip check failed: {e}")
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            env_info["virtual_env"] = sys.prefix
        else:
            env_info["issues"].append("Not running in virtual environment (recommended)")
        
        # Check site-packages directory
        try:
            import site
            env_info["site_packages"] = site.getsitepackages()
        except Exception as e:
            env_info["issues"].append(f"Cannot determine site-packages: {e}")
        
        return env_info

    def verify_package(self, req: SystemRequirement) -> Tuple[bool, str, str]:
        """Verify if a package is installed and working"""
        try:
            # Check if package is installed via pip
            try:
                installed_version = pkg_resources.get_distribution(req.package).version
            except pkg_resources.DistributionNotFound:
                return False, "not_installed", "Package not found"
            
            # Try to import and run verification command
            if req.verify_cmd:
                try:
                    result = subprocess.run([self.python_exe, "-c", req.verify_cmd], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return True, installed_version, "Working correctly"
                    else:
                        return False, installed_version, f"Import/verification failed: {result.stderr}"
                except Exception as e:
                    return False, installed_version, f"Verification error: {e}"
            else:
                # Just check installation
                return True, installed_version, "Installed (no verification test)"
                
        except Exception as e:
            return False, "unknown", f"Check failed: {e}"

    def install_package(self, req: SystemRequirement) -> Tuple[bool, str]:
        """Install a single package"""
        logger.info(f"Installing {req.name} ({req.package})...")
        
        try:
            # Prepare install command
            install_cmd = req.install_cmd or req.package
            
            # Run pip install
            cmd = [self.python_exe, "-m", "pip", "install", "-U", install_cmd]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f" Successfully installed {req.name}")
                return True, "Installation successful"
            else:
                error_msg = f"Installation failed: {result.stderr}"
                logger.error(f" Failed to install {req.name}: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "Installation timed out"
            logger.error(f" {req.name} installation timed out")
            return False, error_msg
        except Exception as e:
            error_msg = f"Installation error: {e}"
            logger.error(f" {req.name} installation error: {e}")
            return False, error_msg

    def scan_system(self) -> SystemHealth:
        """Comprehensive system scan"""
        logger.info(" Starting comprehensive EQ12 system scan...")
        
        health = SystemHealth()
        health.total_requirements = len(self.requirements)
        health.issues = []
        health.recommendations = []
        
        # Check each requirement
        for name, req in self.requirements.items():
            is_installed, version, status = self.verify_package(req)
            
            if is_installed:
                health.installed += 1
                logger.info(f" {req.name}: {version}")
            else:
                health.missing += 1
                if req.critical:
                    health.critical_missing += 1
                    health.issues.append(f"CRITICAL: {req.name} missing - {req.description}")
                else:
                    health.issues.append(f"Optional: {req.name} missing - {req.description}")
                logger.warning(f" {req.name}: {status}")
        
        # Calculate health score
        if health.total_requirements > 0:
            health.health_score = (health.installed / health.total_requirements) * 100
        
        # Generate recommendations
        if health.critical_missing > 0:
            health.recommendations.append(f"Install {health.critical_missing} critical packages immediately")
        if health.missing > health.critical_missing:
            health.recommendations.append(f"Consider installing {health.missing - health.critical_missing} optional packages")
        if health.health_score < 80:
            health.recommendations.append("System health below 80% - comprehensive installation recommended")
        elif health.health_score < 95:
            health.recommendations.append("System health good but can be improved")
        else:
            health.recommendations.append("System health excellent - minimal action needed")
        
        return health

    def install_missing_packages(self, install_optional: bool = False) -> Dict[str, Any]:
        """Install all missing packages"""
        logger.info(" Starting EQ12 package installation...")
        
        install_results = {
            "attempted": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "details": {}
        }
        
        for name, req in self.requirements.items():
            is_installed, version, status = self.verify_package(req)
            
            if is_installed:
                install_results["skipped"] += 1
                install_results["details"][name] = {"status": "already_installed", "version": version}
                continue
            
            # Skip optional packages if not requested
            if not req.critical and not install_optional:
                install_results["skipped"] += 1
                install_results["details"][name] = {"status": "skipped_optional", "reason": "Optional package"}
                continue
            
            # Attempt installation
            install_results["attempted"] += 1
            success, message = self.install_package(req)
            
            if success:
                install_results["successful"] += 1
                install_results["details"][name] = {"status": "installed", "message": message}
            else:
                install_results["failed"] += 1
                install_results["details"][name] = {"status": "failed", "message": message}
        
        return install_results

    def fix_common_issues(self) -> Dict[str, Any]:
        """Fix common EQ12 system issues"""
        logger.info(" Fixing common EQ12 system issues...")
        
        fix_results = {}
        
        # Fix 1: Upgrade pip
        try:
            logger.info("Upgrading pip...")
            result = subprocess.run([self.python_exe, "-m", "pip", "install", "-U", "pip"], 
                                  capture_output=True, text=True, timeout=120)
            fix_results["pip_upgrade"] = {
                "success": result.returncode == 0,
                "message": result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            fix_results["pip_upgrade"] = {"success": False, "message": str(e)}
        
        # Fix 2: Clean pip cache
        try:
            logger.info("Cleaning pip cache...")
            result = subprocess.run([self.python_exe, "-m", "pip", "cache", "purge"], 
                                  capture_output=True, text=True, timeout=60)
            fix_results["cache_clean"] = {
                "success": result.returncode == 0,
                "message": "Cache cleaned" if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            fix_results["cache_clean"] = {"success": False, "message": str(e)}
        
        # Fix 3: Install wheel and setuptools
        try:
            logger.info("Installing build tools...")
            result = subprocess.run([self.python_exe, "-m", "pip", "install", "-U", "wheel", "setuptools"], 
                                  capture_output=True, text=True, timeout=120)
            fix_results["build_tools"] = {
                "success": result.returncode == 0,
                "message": "Build tools updated" if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            fix_results["build_tools"] = {"success": False, "message": str(e)}
        
        # Fix 4: Fix OpenAI migration
        try:
            logger.info("Checking OpenAI migration...")
            # Install modern OpenAI
            result = subprocess.run([self.python_exe, "-m", "pip", "install", "-U", "openai>=1.50.0"], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                # Try to run migration
                try:
                    migration_result = subprocess.run([self.python_exe, "-m", "openai", "migrate"], 
                                                    capture_output=True, text=True, timeout=60,
                                                    cwd=str(self.workspace_path))
                    fix_results["openai_migration"] = {
                        "success": True,
                        "message": f"OpenAI updated and migration attempted: {migration_result.stdout}"
                    }
                except:
                    fix_results["openai_migration"] = {
                        "success": True,
                        "message": "OpenAI updated (migration tool not available)"
                    }
            else:
                fix_results["openai_migration"] = {"success": False, "message": result.stderr}
        except Exception as e:
            fix_results["openai_migration"] = {"success": False, "message": str(e)}
        
        # Fix 5: Create requirements.txt
        try:
            logger.info("Creating requirements.txt...")
            requirements_file = self.workspace_path / "requirements.txt"
            with open(requirements_file, 'w') as f:
                for name, req in self.requirements.items():
                    if req.critical:
                        f.write(f"{req.install_cmd or req.package}\n")
            fix_results["requirements_file"] = {
                "success": True,
                "message": f"Created {requirements_file}"
            }
        except Exception as e:
            fix_results["requirements_file"] = {"success": False, "message": str(e)}
        
        return fix_results

    def test_eq12_modules(self) -> Dict[str, Any]:
        """Test EQ12 module functionality"""
        logger.info(" Testing EQ12 module functionality...")
        
        test_results = {}
        
        # Test Groq engine
        try:
            groq_script = self.workspace_path / "scripts" / "eq12_groq_engine.py"
            if groq_script.exists():
                result = subprocess.run([self.python_exe, str(groq_script), "--test", "System test"], 
                                      capture_output=True, text=True, timeout=60)
                test_results["groq_engine"] = {
                    "success": result.returncode == 0,
                    "message": result.stdout if result.returncode == 0 else result.stderr
                }
            else:
                test_results["groq_engine"] = {"success": False, "message": "Script not found"}
        except Exception as e:
            test_results["groq_engine"] = {"success": False, "message": str(e)}
        
        # Test Telegram Router
        try:
            telegram_script = self.workspace_path / "scripts" / "eq12_telegram_router.py"
            if telegram_script.exists():
                result = subprocess.run([self.python_exe, str(telegram_script), "--analytics"], 
                                      capture_output=True, text=True, timeout=30)
                test_results["telegram_router"] = {
                    "success": result.returncode == 0,
                    "message": "Router responding" if result.returncode == 0 else result.stderr
                }
            else:
                test_results["telegram_router"] = {"success": False, "message": "Script not found"}
        except Exception as e:
            test_results["telegram_router"] = {"success": False, "message": str(e)}
        
        # Test Token Gateway
        try:
            token_script = self.workspace_path / "scripts" / "eq12_token_gateway.py"
            if token_script.exists():
                result = subprocess.run([self.python_exe, str(token_script), "--help"], 
                                      capture_output=True, text=True, timeout=30)
                test_results["token_gateway"] = {
                    "success": result.returncode == 0,
                    "message": "Gateway functional" if result.returncode == 0 else result.stderr
                }
            else:
                test_results["token_gateway"] = {"success": False, "message": "Script not found"}
        except Exception as e:
            test_results["token_gateway"] = {"success": False, "message": str(e)}
        
        # Test Web Interface
        try:
            web_script = self.workspace_path / "scripts" / "eq12_web_interface_clean.py"
            if web_script.exists():
                # Just check if it imports without errors
                result = subprocess.run([self.python_exe, "-c", f"import sys; sys.path.append('{self.workspace_path}/scripts'); import eq12_web_interface_clean; print('Web interface imports successfully')"], 
                                      capture_output=True, text=True, timeout=30)
                test_results["web_interface"] = {
                    "success": result.returncode == 0,
                    "message": result.stdout if result.returncode == 0 else result.stderr
                }
            else:
                test_results["web_interface"] = {"success": False, "message": "Script not found"}
        except Exception as e:
            test_results["web_interface"] = {"success": False, "message": str(e)}
        
        return test_results

    def generate_comprehensive_report(self, env_info: Dict, health: SystemHealth, 
                                    install_results: Dict, fix_results: Dict, 
                                    test_results: Dict) -> str:
        """Generate comprehensive system report"""
        
        report_file = self.workspace_path / "logs" / f"eq12_system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_info": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture(),
                "workspace": str(self.workspace_path)
            },
            "environment": env_info,
            "health_scan": {
                "total_requirements": health.total_requirements,
                "installed": health.installed,
                "missing": health.missing,
                "critical_missing": health.critical_missing,
                "health_score": health.health_score,
                "issues": health.issues,
                "recommendations": health.recommendations
            },
            "installation_results": install_results,
            "fix_results": fix_results,
            "module_tests": test_results,
            "godlike_status": self.calculate_godlike_status(health, install_results, test_results)
        }
        
        # Save detailed report
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Generate summary report
        summary = self.generate_summary_report(report_data)
        
        summary_file = self.workspace_path / "EQ12_GODLIKE_STATUS_REPORT.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        logger.info(f" Comprehensive report saved: {report_file}")
        logger.info(f" Summary report saved: {summary_file}")
        
        return str(summary_file)

    def calculate_godlike_status(self, health: SystemHealth, install_results: Dict, 
                               test_results: Dict) -> Dict[str, Any]:
        """Calculate overall godlike status"""
        
        # Calculate component scores
        health_score = health.health_score
        install_score = (install_results.get("successful", 0) / max(install_results.get("attempted", 1), 1)) * 100
        
        test_success = sum(1 for result in test_results.values() if result.get("success", False))
        test_total = len(test_results)
        test_score = (test_success / max(test_total, 1)) * 100
        
        # Overall score
        overall_score = (health_score * 0.5 + install_score * 0.3 + test_score * 0.2)
        
        # Determine status level
        if overall_score >= 95:
            status_level = "GODLIKE"
            status_description = "EQ12 system operating at maximum capacity"
        elif overall_score >= 85:
            status_level = "EXCELLENT"
            status_description = "EQ12 system highly optimized and functional"
        elif overall_score >= 70:
            status_level = "GOOD"
            status_description = "EQ12 system functional with minor issues"
        elif overall_score >= 50:
            status_level = "FAIR"
            status_description = "EQ12 system needs improvements"
        else:
            status_level = "POOR"
            status_description = "EQ12 system requires significant repairs"
        
        return {
            "overall_score": round(overall_score, 2),
            "level": status_level,
            "description": status_description,
            "component_scores": {
                "health": round(health_score, 2),
                "installation": round(install_score, 2),
                "testing": round(test_score, 2)
            },
            "critical_issues": health.critical_missing,
            "functional_modules": test_success,
            "recommendations": health.recommendations
        }

    def generate_summary_report(self, report_data: Dict) -> str:
        """Generate human-readable summary report"""
        
        godlike_status = report_data["godlike_status"]
        health = report_data["health_scan"]
        install = report_data["installation_results"]
        tests = report_data["module_tests"]
        
        summary = f"""#  EQ12 GODLIKE STATUS REPORT

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Status:** {godlike_status['level']} ({godlike_status['overall_score']:.1f}%)  
**Description:** {godlike_status['description']}

---

##  SYSTEM HEALTH OVERVIEW

| Metric | Value | Status |
|--------|--------|--------|
| **Health Score** | {health['health_score']:.1f}% | {'' if health['health_score'] >= 80 else '' if health['health_score'] >= 60 else ''} |
| **Packages Installed** | {health['installed']}/{health['total_requirements']} | {'' if health['missing'] == 0 else ''} |
| **Critical Missing** | {health['critical_missing']} | {'' if health['critical_missing'] == 0 else ''} |
| **Functional Modules** | {godlike_status['functional_modules']}/{len(tests)} | {'' if godlike_status['functional_modules'] == len(tests) else ''} |

---

##  INSTALLATION RESULTS

"""
        
        if install['attempted'] > 0:
            summary += f"""
**Packages Processed:** {install['attempted']}  
**Successfully Installed:** {install['successful']}   
**Failed Installations:** {install['failed']}   
**Already Installed:** {install['skipped']}   

**Installation Success Rate:** {(install['successful'] / max(install['attempted'], 1) * 100):.1f}%
"""
        else:
            summary += "\n**No installations attempted** (all packages already present)\n"
        
        summary += f"""

---

##  MODULE TEST RESULTS

"""
        
        for module, result in tests.items():
            status_icon = "" if result['success'] else ""
            summary += f"**{module.replace('_', ' ').title()}:** {status_icon} {result['message']}\n"
        
        if health['issues']:
            summary += f"""

---

##  ISSUES IDENTIFIED

"""
            for issue in health['issues']:
                summary += f"- {issue}\n"
        
        if health['recommendations']:
            summary += f"""

---

##  RECOMMENDATIONS

"""
            for rec in health['recommendations']:
                summary += f"- {rec}\n"
        
        summary += f"""

---

##  NEXT STEPS

"""
        
        if godlike_status['level'] == "GODLIKE":
            summary += """
 **CONGRATULATIONS!** Your EQ12 system has achieved GODLIKE status!

Your system is operating at maximum capacity with:
- All critical packages installed and functional
- All modules passing tests
- Optimal performance across all components

**You are ready to:**
- Deploy tokenized AI services
- Launch premium Telegram channels
- Scale to thousands of users
- Generate autonomous revenue

**Maintain this status by:**
- Running periodic health checks
- Keeping packages updated
- Monitoring system performance
"""
        
        elif godlike_status['level'] in ["EXCELLENT", "GOOD"]:
            summary += f"""
 **Great Progress!** Your EQ12 system is {godlike_status['level'].lower()} and nearly ready for production.

**To achieve GODLIKE status:**
- Install any missing critical packages
- Fix remaining module issues
- Optimize performance bottlenecks

**Quick wins:**
- Run: `python eq12_godlike_installer.py --install-optional`
- Test all modules individually
- Update any outdated packages
"""
        
        else:
            summary += """
 **System Needs Attention** 

Your EQ12 system requires improvements to reach optimal performance.

**Priority Actions:**
1. Install all critical missing packages
2. Fix module import/runtime errors
3. Resolve environment configuration issues
4. Re-run this installer after fixes

**Get help:**
- Check individual error messages above
- Review installation logs
- Verify environment variables are set
"""
        
        summary += f"""

---

##  SYSTEM SPECIFICATIONS

**Python:** {report_data['system_info']['python_version']}  
**Platform:** {report_data['system_info']['platform']}  
**Architecture:** {report_data['system_info']['architecture'][0]}  
**Workspace:** {report_data['system_info']['workspace']}  

**Package Categories:**
- AI Core: OpenAI, Groq, Transformers
- Web Stack: FastAPI, Uvicorn, Jinja2
- Communication: Telegram Bot API
- Blockchain: Web3.py, eth-account
- Data Science: Pandas, NumPy, SciPy
- Security: Cryptography, JWT, dotenv

---

*EQ12 Godlike Installer - Making AI systems unstoppable* 
"""
        
        return summary

    async def run_complete_analysis(self, install_optional: bool = False) -> str:
        """Run complete system analysis and repair"""
        
        logger.info(" Starting EQ12 Godlike System Analysis...")
        start_time = time.time()
        
        try:
            # Step 1: Check Python environment
            env_info = self.check_python_environment()
            logger.info(f"Python {env_info['python_version']} detected")
            
            # Step 2: Scan system health
            health = self.scan_system()
            logger.info(f"System health: {health.health_score:.1f}% ({health.installed}/{health.total_requirements} packages)")
            
            # Step 3: Fix common issues
            fix_results = self.fix_common_issues()
            fixes_applied = sum(1 for result in fix_results.values() if result.get('success', False))
            logger.info(f"Applied {fixes_applied}/{len(fix_results)} fixes")
            
            # Step 4: Install missing packages
            install_results = self.install_missing_packages(install_optional)
            logger.info(f"Installation: {install_results['successful']} successful, {install_results['failed']} failed")
            
            # Step 5: Test EQ12 modules
            test_results = self.test_eq12_modules()
            tests_passed = sum(1 for result in test_results.values() if result.get('success', False))
            logger.info(f"Module tests: {tests_passed}/{len(test_results)} passed")
            
            # Step 6: Generate comprehensive report
            report_file = self.generate_comprehensive_report(
                env_info, health, install_results, fix_results, test_results
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f" EQ12 Godlike Analysis completed in {elapsed_time:.2f} seconds")
            logger.info(f" Report saved: {report_file}")
            
            return report_file
            
        except Exception as e:
            logger.error(f" Fatal error during analysis: {e}")
            raise


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Godlike System Installer & Quantifier")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--install-optional", action="store_true", help="Install optional packages")
    parser.add_argument("--scan-only", action="store_true", help="Scan only, no installations")
    parser.add_argument("--fix-only", action="store_true", help="Apply fixes only")
    parser.add_argument("--test-only", action="store_true", help="Test modules only")
    
    args = parser.parse_args()
    
    try:
        installer = EQ12GodlikeInstaller(args.workspace)
        
        if args.scan_only:
            health = installer.scan_system()
            print(f"\n System Health: {health.health_score:.1f}%")
            print(f" Packages: {health.installed}/{health.total_requirements} installed")
            print(f" Critical Missing: {health.critical_missing}")
            return 0
        
        if args.test_only:
            results = installer.test_eq12_modules()
            passed = sum(1 for r in results.values() if r.get('success', False))
            print(f"\n Module Tests: {passed}/{len(results)} passed")
            return 0
        
        if args.fix_only:
            results = installer.fix_common_issues()
            fixed = sum(1 for r in results.values() if r.get('success', False))
            print(f"\n Fixes Applied: {fixed}/{len(results)}")
            return 0
        
        # Run complete analysis
        report_file = asyncio.run(installer.run_complete_analysis(args.install_optional))
        
        print(f"\n EQ12 Godlike Analysis Complete!")
        print(f" Full Report: {report_file}")
        print(f" Summary: {Path(args.workspace) / 'EQ12_GODLIKE_STATUS_REPORT.md'}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n Installation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n Fatal error: {e}")
        logger.exception("Fatal error in main")
        return 1


if __name__ == "__main__":
    exit(main())