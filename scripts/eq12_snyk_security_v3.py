#!/usr/bin/env python3
"""
EQ12 Security Scanner v3.0 - Clean, Stable, Memory-Safe
Comprehensive security scanning with robust error handling and resource management
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import subprocess
import sys
import atexit
import psutil
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

# Configure logging with rotation
from logging.handlers import RotatingFileHandler

logs_dir = Path("C:/EQ12/logs")
logs_dir.mkdir(exist_ok=True)

# Setup rotating log handler
log_handler = RotatingFileHandler(
    logs_dir / "snyk_security.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
log_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(logging.StreamHandler())


@dataclass
class SecurityVulnerability:
    """Structured vulnerability representation"""
    id: str
    severity: str
    title: str
    description: str
    file_path: Optional[str]
    line_number: Optional[int]
    cwe: Optional[str]
    cvss_score: Optional[float]
    fix_guidance: Optional[str]
    package_name: Optional[str]
    package_version: Optional[str]
    scan_type: str
    detected_at: str


@dataclass
class SecurityScanResult:
    """Comprehensive security scan results"""
    scan_id: str
    project_path: str
    scan_timestamp: str
    scan_types: list[str]
    total_vulnerabilities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    vulnerabilities: list[SecurityVulnerability]
    scan_metadata: dict[str, Any]
    recommendations: list[str]


class EQ12SecurityScanner:
    """Memory-safe, robust security scanner for EQ12"""

    def __init__(self):
        self.project_root = Path("C:/EQ12")
        self.logs_dir = logs_dir
        self.config_dir = self.project_root / "configs"
        
        # Lock and PID management
        self.lock_file = self.logs_dir / "eq12_security.lock"
        self.pid_file = self.logs_dir / "eq12_security.pid"
        
        # Memory and performance limits
        self.memory_limit_mb = 1024
        self.cpu_limit_percent = 70
        self.scan_timeout = 300  # 5 minutes per scan type
        
        # Safe scan targets (excluding heavy directories)
        self.scan_targets = {
            "scripts": self.project_root / "scripts",
            "tests": self.project_root / "tests",
            "configs": self.project_root / "configs",
        }
        
        # Heavy directories to exclude
        self.excludes = [
            "node_modules", "build", "dist", ".git", "logs", "data", 
            ".venv", "venv", "__pycache__", "stable-diffusion-webui",
            "ComfyUI", "ai_image_generation", "web3_repos", "research",
            "sdk_development", "mcp_servers", "groq-api-cookbook"
        ]
        
        # Register cleanup
        atexit.register(self._cleanup)
        
        logger.info("EQ12 Security Scanner v3.0 initialized")

    def _cleanup(self):
        """Ensure clean shutdown"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception:
            pass

    async def acquire_lock(self) -> bool:
        """Acquire exclusive execution lock"""
        try:
            if self.lock_file.exists():
                # Check if process is still running
                try:
                    pid_content = self.lock_file.read_text().strip()
                    if pid_content.isdigit():
                        old_pid = int(pid_content)
                        if psutil.pid_exists(old_pid):
                            logger.warning(f"Another scanner running (PID {old_pid})")
                            return False
                except Exception:
                    pass
                # Remove stale lock
                self.lock_file.unlink(missing_ok=True)
            
            # Create new lock
            current_pid = os.getpid()
            self.lock_file.write_text(str(current_pid))
            self.pid_file.write_text(str(current_pid))
            logger.info(f"Acquired lock (PID {current_pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to acquire lock: {e}")
            return False

    async def check_system_resources(self) -> bool:
        """Verify system has sufficient resources"""
        try:
            # Check available memory
            memory = psutil.virtual_memory()
            available_mb = memory.available // (1024 * 1024)
            
            if available_mb < self.memory_limit_mb + 512:  # Need buffer
                logger.error(f"Insufficient memory: {available_mb}MB available, need {self.memory_limit_mb + 512}MB")
                return False
            
            # Check CPU load
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                logger.warning(f"High CPU load: {cpu_percent}%")
                
            logger.info(f"System resources OK: {available_mb}MB RAM, {cpu_percent}% CPU")
            return True
            
        except Exception as e:
            logger.error(f"Resource check failed: {e}")
            return False

    async def kill_memory_hogs(self):
        """Terminate processes consuming excessive memory"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
                    
                    # Kill runaway Docker processes
                    if proc.info['name'].lower() in ['docker', 'dockerd'] and mem_mb > 2048:
                        logger.warning(f"Killing memory-heavy Docker process: {proc.info['name']} ({mem_mb:.0f}MB)")
                        proc.kill()
                        
                    # Kill runaway WSL processes
                    elif proc.info['name'].lower() in ['wsl', 'wslhost'] and mem_mb > 1536:
                        logger.warning(f"Killing memory-heavy WSL process: {proc.info['name']} ({mem_mb:.0f}MB)")
                        proc.kill()
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")

    async def run_snyk_command(self, cmd: list[str], cwd: Path) -> tuple[bool, str]:
        """Run a single Snyk command with resource monitoring"""
        try:
            exclude_arg = ",".join(self.excludes)
            full_cmd = cmd + [f"--exclude={exclude_arg}"]
            
            logger.info(f"Running: {' '.join(full_cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *full_cmd,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor process resources
            start_time = time.time()
            monitor_task = asyncio.create_task(self._monitor_process(process.pid))
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.scan_timeout
                )
                
                monitor_task.cancel()
                duration = time.time() - start_time
                
                logger.info(f"Command completed in {duration:.1f}s with exit code {process.returncode}")
                
                if stdout:
                    return True, stdout.decode('utf-8', errors='ignore')
                else:
                    return False, stderr.decode('utf-8', errors='ignore') if stderr else "No output"
                    
            except asyncio.TimeoutError:
                logger.error(f"Command timeout after {self.scan_timeout}s")
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                monitor_task.cancel()
                return False, f"Timeout after {self.scan_timeout}s"
                
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return False, str(e)

    async def _monitor_process(self, pid: int):
        """Monitor process resource usage"""
        try:
            process = psutil.Process(pid)
            
            while True:
                try:
                    mem_mb = process.memory_info().rss / (1024 * 1024)
                    cpu_percent = process.cpu_percent()
                    
                    if mem_mb > self.memory_limit_mb * 1.5:  # 150% of limit
                        logger.error(f"Process {pid} exceeded memory limit: {mem_mb:.0f}MB")
                        process.kill()
                        break
                        
                    if cpu_percent > self.cpu_limit_percent:
                        logger.warning(f"Process {pid} high CPU: {cpu_percent:.1f}%")
                        
                    await asyncio.sleep(5)  # Check every 5 seconds
                    
                except psutil.NoSuchProcess:
                    break
                    
        except Exception:
            pass

    async def scan_with_snyk(self) -> SecurityScanResult:
        """Perform comprehensive but safe Snyk scan"""
        scan_id = hashlib.md5(f"eq12_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        all_vulnerabilities = []
        scan_types = []
        
        for target_name, target_path in self.scan_targets.items():
            if not target_path.exists():
                logger.warning(f"Target path missing: {target_path}")
                continue
                
            logger.info(f"Scanning {target_name}: {target_path}")
            
            # Snyk Code scan (SAST)
            success, output = await self.run_snyk_command(
                ["snyk", "code", "test", str(target_path), "--json"],
                target_path
            )
            
            if success and output:
                vulns = self._parse_snyk_code_output(output, target_name)
                all_vulnerabilities.extend(vulns)
                if vulns:
                    scan_types.append("SAST")
            
            # Small delay between scans
            await asyncio.sleep(2)
            
            # Snyk Open Source scan (SCA) - only on directories with package files
            if any((target_path / f).exists() for f in ["package.json", "requirements.txt", "pyproject.toml"]):
                success, output = await self.run_snyk_command(
                    ["snyk", "test", str(target_path), "--json"],
                    target_path
                )
                
                if success and output:
                    vulns = self._parse_snyk_os_output(output, target_name)
                    all_vulnerabilities.extend(vulns)
                    if vulns:
                        scan_types.append("SCA")
        
        # Count by severity
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for vuln in all_vulnerabilities:
            severity = vuln.severity.upper()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return SecurityScanResult(
            scan_id=scan_id,
            project_path=str(self.project_root),
            scan_timestamp=datetime.now(UTC).isoformat(),
            scan_types=list(set(scan_types)),
            total_vulnerabilities=len(all_vulnerabilities),
            critical_count=severity_counts["CRITICAL"],
            high_count=severity_counts["HIGH"],
            medium_count=severity_counts["MEDIUM"],
            low_count=severity_counts["LOW"],
            vulnerabilities=all_vulnerabilities,
            scan_metadata={
                "version": "3.0",
                "memory_limit_mb": self.memory_limit_mb,
                "targets_scanned": list(self.scan_targets.keys()),
                "excludes": self.excludes
            },
            recommendations=self._generate_recommendations(all_vulnerabilities)
        )

    def _parse_snyk_code_output(self, output: str, target: str) -> list[SecurityVulnerability]:
        """Parse Snyk Code JSON output"""
        vulnerabilities = []
        try:
            data = json.loads(output)
            if "runs" in data:
                for run in data["runs"]:
                    for result in run.get("results", []):
                        vuln = SecurityVulnerability(
                            id=result.get("ruleId", "UNKNOWN"),
                            severity=result.get("level", "unknown").upper(),
                            title=result.get("message", {}).get("text", "Code vulnerability"),
                            description=result.get("message", {}).get("text", ""),
                            file_path=self._extract_file_path(result),
                            line_number=self._extract_line_number(result),
                            cwe=None,
                            cvss_score=None,
                            fix_guidance="Review code and apply secure coding practices",
                            package_name=None,
                            package_version=None,
                            scan_type="SAST",
                            detected_at=datetime.now(UTC).isoformat()
                        )
                        vulnerabilities.append(vuln)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Snyk Code output: {e}")
        
        return vulnerabilities

    def _parse_snyk_os_output(self, output: str, target: str) -> list[SecurityVulnerability]:
        """Parse Snyk Open Source JSON output"""
        vulnerabilities = []
        try:
            data = json.loads(output)
            for vuln_data in data.get("vulnerabilities", []):
                vuln = SecurityVulnerability(
                    id=vuln_data.get("id", "UNKNOWN"),
                    severity=vuln_data.get("severity", "unknown").upper(),
                    title=vuln_data.get("title", "Dependency vulnerability"),
                    description=vuln_data.get("description", ""),
                    file_path=vuln_data.get("from", [None])[0] if vuln_data.get("from") else None,
                    line_number=None,
                    cwe=None,
                    cvss_score=vuln_data.get("cvssScore"),
                    fix_guidance=self._extract_fix_guidance(vuln_data),
                    package_name=vuln_data.get("packageName"),
                    package_version=vuln_data.get("version"),
                    scan_type="SCA",
                    detected_at=datetime.now(UTC).isoformat()
                )
                vulnerabilities.append(vuln)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Snyk OS output: {e}")
        
        return vulnerabilities

    def _extract_file_path(self, result: dict) -> Optional[str]:
        """Extract file path from Snyk result"""
        try:
            if "locations" in result and result["locations"]:
                location = result["locations"][0]
                if "physicalLocation" in location:
                    return location["physicalLocation"]["artifactLocation"]["uri"]
        except (KeyError, IndexError):
            pass
        return None

    def _extract_line_number(self, result: dict) -> Optional[int]:
        """Extract line number from Snyk result"""
        try:
            if "locations" in result and result["locations"]:
                location = result["locations"][0]
                if "physicalLocation" in location:
                    region = location["physicalLocation"].get("region", {})
                    return region.get("startLine")
        except (KeyError, IndexError):
            pass
        return None

    def _extract_fix_guidance(self, vuln_data: dict) -> str:
        """Extract fix guidance from vulnerability data"""
        if "fixes" in vuln_data and vuln_data["fixes"]:
            return f"Update to version {vuln_data['fixes'][0].get('version', 'latest')}"
        return "No automated fix available"

    def _generate_recommendations(self, vulnerabilities: list[SecurityVulnerability]) -> list[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if not vulnerabilities:
            recommendations.append("No vulnerabilities found - maintain current security practices")
        else:
            critical_count = sum(1 for v in vulnerabilities if v.severity == "CRITICAL")
            high_count = sum(1 for v in vulnerabilities if v.severity == "HIGH")
            
            if critical_count > 0:
                recommendations.append(f"URGENT: Address {critical_count} critical vulnerabilities immediately")
            
            if high_count > 0:
                recommendations.append(f"Address {high_count} high-severity vulnerabilities within 7 days")
            
            recommendations.extend([
                "Enable automated dependency scanning in CI/CD",
                "Implement regular security training for development team",
                "Consider implementing Snyk monitoring for continuous scanning"
            ])
        
        return recommendations

    async def save_report(self, scan_result: SecurityScanResult) -> str:
        """Save scan results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.logs_dir / f"security_report_{timestamp}.json"
        
        report_data = {
            "metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "scanner_version": "3.0",
                "eq12_version": "1.0"
            },
            "executive_summary": {
                "total_vulnerabilities": scan_result.total_vulnerabilities,
                "critical": scan_result.critical_count,
                "high": scan_result.high_count,
                "medium": scan_result.medium_count,
                "low": scan_result.low_count
            },
            "scan_results": asdict(scan_result)
        }
        
        report_path.write_text(json.dumps(report_data, indent=2), encoding='utf-8')
        logger.info(f"Report saved: {report_path}")
        return str(report_path)


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 Security Scanner v3.0")
    parser.add_argument("--scan", action="store_true", help="Run security scan")
    parser.add_argument("--clean-memory", action="store_true", help="Clean memory hogs before scan")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    scanner = EQ12SecurityScanner()
    
    try:
        # Acquire exclusive lock
        if not await scanner.acquire_lock():
            logger.error("Another scan is already running")
            return 1
        
        # Clean memory if requested
        if args.clean_memory:
            logger.info("Cleaning memory hogs...")
            await scanner.kill_memory_hogs()
            await asyncio.sleep(5)  # Let system stabilize
        
        # Check system resources
        if not await scanner.check_system_resources():
            logger.error("Insufficient system resources")
            return 1
        
        if args.scan:
            logger.info(" Starting EQ12 Security Scan v3.0")
            scan_result = await scanner.scan_with_snyk()
            
            # Save report
            report_path = await scanner.save_report(scan_result)
            
            # Display summary
            print("\n" + "="*60)
            print(" EQ12 SECURITY SCAN RESULTS")
            print("="*60)
            print(f" Total Vulnerabilities: {scan_result.total_vulnerabilities}")
            print(f" Critical: {scan_result.critical_count}")
            print(f"  High: {scan_result.high_count}")
            print(f" Medium: {scan_result.medium_count}")
            print(f"  Low: {scan_result.low_count}")
            print(f" Report: {report_path}")
            print("="*60)
            
            if scan_result.critical_count > 0:
                return 2
            elif scan_result.high_count > 5:
                return 1
            else:
                return 0
        
        parser.print_help()
        return 0
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))