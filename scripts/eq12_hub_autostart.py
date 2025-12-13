#!/usr/bin/env python3
"""
EQ12 Hub Autostart Service
Persistent service manager for the complete EQ12 autonomous ecosystem.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import psutil
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\hub_autostart.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12HubService:
    """EQ12 Hub Autostart Service - Persistent ecosystem manager"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.services = {}
        self.running = False
        
        # Service definitions
        self.service_configs = {
            "web_interface": {
                "script": "scripts/eq12_web_interface_clean.py",
                "args": ["--persistent", "--host", "0.0.0.0", "--port", "8080"],
                "restart_delay": 5,
                "max_restarts": 10,
                "critical": True
            },
            "wealth_core": {
                "script": "scripts/eq12_wealth_core.py",
                "args": ["--daemon", "--workspace", str(self.workspace_path)],
                "restart_delay": 10,
                "max_restarts": 5,
                "critical": True
            },
            "openai_monitor": {
                "script": "scripts/eq12_openai_key_engine.py",
                "args": ["--monitor", "--workspace", str(self.workspace_path)],
                "restart_delay": 15,
                "max_restarts": 3,
                "critical": False
            },
            "groq_engine": {
                "script": "scripts/eq12_groq_engine.py",
                "args": ["--monitor", "--workspace", str(self.workspace_path)],
                "restart_delay": 8,
                "max_restarts": 5,
                "critical": False
            }
        }
        
        # Paths
        self.pid_dir = self.workspace_path / "temp"
        self.log_dir = self.workspace_path / "logs"
        
        # Create directories
        self.pid_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("EQ12 Hub Autostart Service initialized")

    def start_service(self, service_name: str) -> bool:
        """Start a specific EQ12 service"""
        try:
            if service_name in self.services:
                logger.warning(f"Service {service_name} already running")
                return True
            
            config = self.service_configs.get(service_name)
            if not config:
                logger.error(f"Unknown service: {service_name}")
                return False
            
            script_path = self.workspace_path / config["script"]
            if not script_path.exists():
                logger.error(f"Script not found: {script_path}")
                return False
            
            # Build command
            cmd = ["python", str(script_path)] + config["args"]
            
            # Start process
            log_file = self.log_dir / f"{service_name}.log"
            with open(log_file, 'a') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=self.workspace_path,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
            
            # Store service info
            self.services[service_name] = {
                "process": process,
                "config": config,
                "start_time": datetime.now(timezone.utc),
                "restart_count": 0,
                "last_restart": None
            }
            
            # Save PID
            pid_file = self.pid_dir / f"{service_name}.pid"
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            logger.info(f"Started service {service_name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service {service_name}: {e}")
            return False

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific EQ12 service"""
        try:
            if service_name not in self.services:
                logger.warning(f"Service {service_name} not running")
                return True
            
            service = self.services[service_name]
            process = service["process"]
            
            # Graceful shutdown
            if os.name == 'nt':
                process.terminate()
            else:
                process.send_signal(signal.SIGTERM)
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                process.kill()
                process.wait()
            
            # Clean up
            del self.services[service_name]
            
            # Remove PID file
            pid_file = self.pid_dir / f"{service_name}.pid"
            if pid_file.exists():
                pid_file.unlink()
            
            logger.info(f"Stopped service {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop service {service_name}: {e}")
            return False

    def restart_service(self, service_name: str) -> bool:
        """Restart a specific EQ12 service"""
        logger.info(f"Restarting service {service_name}")
        
        if service_name in self.services:
            service = self.services[service_name]
            service["restart_count"] += 1
            service["last_restart"] = datetime.now(timezone.utc)
            
            # Check restart limits
            if service["restart_count"] > service["config"]["max_restarts"]:
                logger.error(f"Service {service_name} exceeded max restarts, marking as failed")
                return False
        
        success = self.stop_service(service_name)
        if not success:
            return False
        
        # Wait before restart
        config = self.service_configs.get(service_name, {})
        delay = config.get("restart_delay", 5)
        time.sleep(delay)
        
        return self.start_service(service_name)

    def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        try:
            if service_name not in self.services:
                return False
            
            service = self.services[service_name]
            process = service["process"]
            
            # Check if process is still running
            if process.poll() is not None:
                logger.warning(f"Service {service_name} process died")
                return False
            
            # Additional health checks could go here
            # (e.g., HTTP health endpoint checks)
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return False

    def monitor_services(self):
        """Monitor all services and restart if needed"""
        logger.info("Starting service monitoring loop")
        
        while self.running:
            try:
                for service_name in list(self.services.keys()):
                    if not self.check_service_health(service_name):
                        config = self.service_configs.get(service_name, {})
                        
                        if config.get("critical", False):
                            logger.error(f"Critical service {service_name} failed, restarting")
                            self.restart_service(service_name)
                        else:
                            logger.warning(f"Non-critical service {service_name} failed")
                            self.stop_service(service_name)
                
                # Send status update
                self.send_status_update()
                
                # Sleep between checks
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(60)

    def start_all_services(self) -> bool:
        """Start all EQ12 services"""
        logger.info("Starting all EQ12 services...")
        
        success_count = 0
        for service_name in self.service_configs.keys():
            if self.start_service(service_name):
                success_count += 1
                # Small delay between service starts
                time.sleep(2)
        
        logger.info(f"Started {success_count}/{len(self.service_configs)} services")
        return success_count == len(self.service_configs)

    def stop_all_services(self) -> bool:
        """Stop all EQ12 services"""
        logger.info("Stopping all EQ12 services...")
        
        success_count = 0
        for service_name in list(self.services.keys()):
            if self.stop_service(service_name):
                success_count += 1
        
        logger.info(f"Stopped {success_count} services")
        return True

    def get_status(self) -> Dict:
        """Get status of all services"""
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hub_running": self.running,
            "services": {},
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_free_gb": psutil.disk_usage(str(self.workspace_path)).free / (1024**3)
            }
        }
        
        for service_name, service in self.services.items():
            process = service["process"]
            
            try:
                proc_info = psutil.Process(process.pid)
                status["services"][service_name] = {
                    "running": process.poll() is None,
                    "pid": process.pid,
                    "start_time": service["start_time"],
                    "restart_count": service["restart_count"],
                    "cpu_percent": proc_info.cpu_percent(),
                    "memory_mb": proc_info.memory_info().rss / (1024**2)
                }
            except psutil.NoSuchProcess:
                status["services"][service_name] = {
                    "running": False,
                    "pid": process.pid,
                    "start_time": service["start_time"],
                    "restart_count": service["restart_count"],
                    "error": "Process not found"
                }
        
        return status

    def send_status_update(self):
        """Send periodic status updates via Telegram"""
        try:
            # This would integrate with your existing Telegram system
            status = self.get_status()
            
            running_services = len([s for s in status["services"].values() if s.get("running", False)])
            total_services = len(status["services"])
            
            if running_services < total_services:
                # Send alert for failed services
                message = f" EQ12 Hub Alert\n"
                message += f"Services: {running_services}/{total_services} running\n"
                message += f"CPU: {status['system']['cpu_percent']:.1f}%\n"
                message += f"Memory: {status['system']['memory_percent']:.1f}%"
                
                # Log the alert (in production, send to Telegram)
                logger.warning(f"Service alert: {message}")
            
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")

    async def run_hub(self):
        """Main hub execution loop"""
        self.running = True
        logger.info("EQ12 Hub Service starting...")
        
        try:
            # Start all services
            self.start_all_services()
            
            # Run monitoring in background
            monitor_task = asyncio.create_task(
                asyncio.to_thread(self.monitor_services)
            )
            
            # Keep hub running
            while self.running:
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
        except Exception as e:
            logger.error(f"Hub error: {e}")
        finally:
            self.running = False
            self.stop_all_services()
            logger.info("EQ12 Hub Service stopped")

    def install_as_service(self):
        """Install as Windows service (placeholder)"""
        # This would implement Windows service installation
        logger.info("Service installation not yet implemented")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Hub Autostart Service")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--start", action="store_true", help="Start all services")
    parser.add_argument("--stop", action="store_true", help="Stop all services")
    parser.add_argument("--restart", action="store_true", help="Restart all services")
    parser.add_argument("--status", action="store_true", help="Show service status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--service", help="Operate on specific service")
    
    args = parser.parse_args()
    
    hub = EQ12HubService(args.workspace)
    
    if args.status:
        status = hub.get_status()
        print(json.dumps(status, indent=2))
        return 0
    
    if args.start:
        if args.service:
            success = hub.start_service(args.service)
        else:
            success = hub.start_all_services()
        return 0 if success else 1
    
    if args.stop:
        if args.service:
            success = hub.stop_service(args.service)
        else:
            success = hub.stop_all_services()
        return 0 if success else 1
    
    if args.restart:
        if args.service:
            success = hub.restart_service(args.service)
        else:
            hub.stop_all_services()
            time.sleep(5)
            success = hub.start_all_services()
        return 0 if success else 1
    
    if args.daemon:
        try:
            asyncio.run(hub.run_hub())
        except KeyboardInterrupt:
            logger.info("Hub daemon stopped")
        except Exception as e:
            logger.error(f"Hub daemon failed: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())