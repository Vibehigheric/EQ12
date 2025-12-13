#!/usr/bin/env python3
"""
 EQ12 CORAL CRYPTO AUTOMATION SUITE
Comprehensive cryptocurrency automation with Google Coral Edge TPU
Master control script for all crypto intelligence operations
"""

import os
import sys
import json
import time
import logging
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess


class CoralCryptoMaster:
    """
     Master control system for EQ12 Coral Crypto Intelligence
    Orchestrates all components: AI engine, data streams, alerts, reports
    """
    
    def __init__(self, config_path: str = None, verbose: bool = False):
        self.setup_logging(verbose)
        
        # Configuration
        self.config = self._load_config(config_path)
        self.workspace_path = "C:\\EQ12"
        
        # Component status
        self.components = {
            "coral_ai": {"script": "eq12_coral_crypto_ai.py", "process": None, "status": "stopped"},
            "data_stream": {"script": "eq12_crypto_stream.py", "process": None, "status": "stopped"},
            "alerts": {"script": "eq12_alerts.py", "process": None, "status": "stopped"},
            "model_updater": {"script": "eq12_model_updater.py", "process": None, "status": "stopped"}
        }
        
        # Performance metrics
        self.metrics = {
            "start_time": None,
            "total_signals": 0,
            "successful_alerts": 0,
            "system_uptime": 0
        }
        
        self.logger.info(" EQ12 Coral Crypto Master initialized")
    
    def setup_logging(self, verbose: bool = False):
        """Setup comprehensive logging"""
        
        log_dir = "C:\\EQ12\\logs\\crypto\\master"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"crypto_master_{timestamp}.log")
        
        level = logging.DEBUG if verbose else logging.INFO
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load master configuration"""
        
        default_config = {
            "automation": {
                "auto_start_components": True,
                "restart_on_failure": True,
                "health_check_interval": 30,
                "max_restart_attempts": 3
            },
            "components": {
                "coral_ai": {
                    "enabled": True,
                    "priority": 1,
                    "restart_delay": 10
                },
                "data_stream": {
                    "enabled": True,
                    "priority": 2,
                    "restart_delay": 5
                },
                "alerts": {
                    "enabled": True,
                    "priority": 3,
                    "restart_delay": 3
                },
                "model_updater": {
                    "enabled": False,  # Manual trigger only
                    "priority": 4,
                    "restart_delay": 60
                }
            },
            "monitoring": {
                "system_metrics": True,
                "component_health": True,
                "performance_alerts": True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def start_component(self, component_name: str) -> bool:
        """Start a specific component"""
        
        if component_name not in self.components:
            self.logger.error(f"Unknown component: {component_name}")
            return False
        
        component = self.components[component_name]
        
        if component["status"] == "running":
            self.logger.info(f"Component {component_name} already running")
            return True
        
        script_path = os.path.join(self.workspace_path, "scripts", component["script"])
        
        if not os.path.exists(script_path):
            self.logger.error(f"Script not found: {script_path}")
            return False
        
        try:
            self.logger.info(f" Starting component: {component_name}")
            
            # Start process
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(script_path)
            )
            
            component["process"] = process
            component["status"] = "running"
            component["start_time"] = datetime.now()
            
            self.logger.info(f" Component {component_name} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f" Failed to start {component_name}: {e}")
            component["status"] = "failed"
            return False
    
    def stop_component(self, component_name: str) -> bool:
        """Stop a specific component"""
        
        if component_name not in self.components:
            self.logger.error(f"Unknown component: {component_name}")
            return False
        
        component = self.components[component_name]
        
        if component["status"] != "running" or component["process"] is None:
            self.logger.info(f"Component {component_name} not running")
            return True
        
        try:
            self.logger.info(f" Stopping component: {component_name}")
            
            process = component["process"]
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if necessary
                process.kill()
                process.wait()
            
            component["process"] = None
            component["status"] = "stopped"
            
            self.logger.info(f" Component {component_name} stopped")
            return True
            
        except Exception as e:
            self.logger.error(f" Failed to stop {component_name}: {e}")
            return False
    
    def check_component_health(self, component_name: str) -> Dict[str, Any]:
        """Check health of a specific component"""
        
        component = self.components[component_name]
        health_status = {
            "component": component_name,
            "status": component["status"],
            "healthy": False,
            "uptime": 0,
            "cpu_usage": 0,
            "memory_usage": 0
        }
        
        if component["status"] != "running" or component["process"] is None:
            return health_status
        
        process = component["process"]
        
        try:
            # Check if process is still alive
            if process.poll() is not None:
                # Process has terminated
                component["status"] = "failed"
                self.logger.warning(f" Component {component_name} has stopped unexpectedly")
                return health_status
            
            # Calculate uptime
            if "start_time" in component:
                uptime = (datetime.now() - component["start_time"]).total_seconds()
                health_status["uptime"] = uptime
            
            health_status["healthy"] = True
            health_status["pid"] = process.pid
            
        except Exception as e:
            self.logger.error(f"Health check failed for {component_name}: {e}")
        
        return health_status
    
    def restart_component(self, component_name: str) -> bool:
        """Restart a specific component"""
        
        self.logger.info(f" Restarting component: {component_name}")
        
        # Stop component
        self.stop_component(component_name)
        
        # Wait for restart delay
        restart_delay = self.config["components"].get(component_name, {}).get("restart_delay", 5)
        time.sleep(restart_delay)
        
        # Start component
        return self.start_component(component_name)
    
    def start_all_components(self) -> Dict[str, bool]:
        """Start all enabled components"""
        
        self.logger.info(" Starting all enabled components...")
        
        results = {}
        
        # Sort components by priority
        component_priority = []
        for name, component in self.components.items():
            config = self.config["components"].get(name, {})
            if config.get("enabled", True):
                priority = config.get("priority", 99)
                component_priority.append((priority, name))
        
        component_priority.sort()  # Sort by priority (lower number = higher priority)
        
        # Start components in priority order
        for priority, component_name in component_priority:
            success = self.start_component(component_name)
            results[component_name] = success
            
            if success:
                # Small delay between component starts
                time.sleep(2)
        
        successful_starts = sum(1 for success in results.values() if success)
        total_components = len(results)
        
        self.logger.info(f" Started {successful_starts}/{total_components} components")
        
        return results
    
    def stop_all_components(self) -> Dict[str, bool]:
        """Stop all running components"""
        
        self.logger.info(" Stopping all components...")
        
        results = {}
        
        for component_name in self.components.keys():
            success = self.stop_component(component_name)
            results[component_name] = success
        
        return results
    
    async def monitor_system(self):
        """Continuous system monitoring and health checks"""
        
        self.logger.info(" Starting system monitoring...")
        self.metrics["start_time"] = datetime.now()
        
        health_check_interval = self.config["automation"]["health_check_interval"]
        restart_on_failure = self.config["automation"]["restart_on_failure"]
        max_restart_attempts = self.config["automation"]["max_restart_attempts"]
        
        restart_attempts = {name: 0 for name in self.components.keys()}
        
        while True:
            try:
                # Check health of all components
                all_healthy = True
                
                for component_name in self.components.keys():
                    health = self.check_component_health(component_name)
                    
                    if not health["healthy"] and self.config["components"].get(component_name, {}).get("enabled", True):
                        all_healthy = False
                        
                        # Attempt restart if enabled
                        if restart_on_failure and restart_attempts[component_name] < max_restart_attempts:
                            self.logger.warning(f" Unhealthy component {component_name}, attempting restart...")
                            
                            if self.restart_component(component_name):
                                restart_attempts[component_name] += 1
                                self.logger.info(f" Successfully restarted {component_name}")
                            else:
                                self.logger.error(f" Failed to restart {component_name}")
                        
                        elif restart_attempts[component_name] >= max_restart_attempts:
                            self.logger.error(f" Component {component_name} exceeded max restart attempts")
                    
                    elif health["healthy"]:
                        # Reset restart attempts on successful health check
                        restart_attempts[component_name] = 0
                
                # Update system metrics
                if self.metrics["start_time"]:
                    self.metrics["system_uptime"] = (datetime.now() - self.metrics["start_time"]).total_seconds()
                
                # Log system status
                if all_healthy:
                    self.logger.debug(f" All components healthy - Uptime: {self.metrics['system_uptime']:.0f}s")
                else:
                    self.logger.warning(" Some components unhealthy")
                
                # Wait for next health check
                await asyncio.sleep(health_check_interval)
                
            except Exception as e:
                self.logger.error(f" System monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        component_health = {}
        for component_name in self.components.keys():
            component_health[component_name] = self.check_component_health(component_name)
        
        return {
            "system_uptime": self.metrics.get("system_uptime", 0),
            "total_components": len(self.components),
            "running_components": sum(1 for health in component_health.values() if health["healthy"]),
            "component_health": component_health,
            "metrics": self.metrics,
            "workspace_path": self.workspace_path
        }
    
    def generate_status_report(self) -> str:
        """Generate formatted status report"""
        
        status = self.get_system_status()
        
        report = f"""
 EQ12 CORAL CRYPTO INTELLIGENCE - SYSTEM STATUS


  System Uptime: {status['system_uptime']:.0f} seconds
 Components: {status['running_components']}/{status['total_components']} running

 COMPONENT STATUS:
"""
        
        for component_name, health in status["component_health"].items():
            status_emoji = "" if health["healthy"] else ""
            uptime_str = f"{health['uptime']:.0f}s" if health["uptime"] > 0 else "N/A"
            
            report += f"   {status_emoji} {component_name}: {health['status']} (uptime: {uptime_str})\n"
        
        report += f"""
 Workspace: {status['workspace_path']}
 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report


async def main():
    """Main function for Coral Crypto Master"""
    
    parser = argparse.ArgumentParser(description="EQ12 Coral Crypto Master Control")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--action", choices=["start", "stop", "restart", "status", "monitor"], 
                       default="monitor", help="Action to perform")
    parser.add_argument("--component", help="Specific component to control")
    
    args = parser.parse_args()
    
    # Initialize master controller
    master = CoralCryptoMaster(config_path=args.config, verbose=args.verbose)
    
    print(" EQ12 CORAL CRYPTO INTELLIGENCE MASTER")
    print("=" * 50)
    
    if args.action == "start":
        if args.component:
            success = master.start_component(args.component)
            print(f"Component {args.component}: {' Started' if success else ' Failed'}")
        else:
            results = master.start_all_components()
            for component, success in results.items():
                print(f"{component}: {' Started' if success else ' Failed'}")
    
    elif args.action == "stop":
        if args.component:
            success = master.stop_component(args.component)
            print(f"Component {args.component}: {' Stopped' if success else ' Failed'}")
        else:
            results = master.stop_all_components()
            for component, success in results.items():
                print(f"{component}: {' Stopped' if success else ' Failed'}")
    
    elif args.action == "restart":
        if args.component:
            success = master.restart_component(args.component)
            print(f"Component {args.component}: {' Restarted' if success else ' Failed'}")
        else:
            print("Restarting all components...")
            master.stop_all_components()
            time.sleep(5)
            results = master.start_all_components()
            for component, success in results.items():
                print(f"{component}: {' Restarted' if success else ' Failed'}")
    
    elif args.action == "status":
        report = master.generate_status_report()
        print(report)
    
    elif args.action == "monitor":
        # Start all components first if auto-start is enabled
        if master.config["automation"]["auto_start_components"]:
            print(" Auto-starting components...")
            results = master.start_all_components()
            
            successful_starts = sum(1 for success in results.values() if success)
            print(f" {successful_starts}/{len(results)} components started successfully")
        
        # Start monitoring
        print("\n Starting continuous monitoring...")
        print("Press Ctrl+C to stop")
        
        try:
            await master.monitor_system()
        except KeyboardInterrupt:
            print("\n Stopping system...")
            master.stop_all_components()
            print(" System stopped")


if __name__ == "__main__":
    asyncio.run(main())