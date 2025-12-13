#!/usr/bin/env python3
"""
 EQ12 UNIFIED SYSTEM INTEGRATION LAUNCHER
===========================================

Advanced unified launcher that integrates all EQ12 systems into a cohesive
multi-tier architecture with seamless orchestration and maximum reliability.

Integrated Systems:
- Daily Maintenance Pack (autonomous health monitoring)
- Self-Healing Orchestrator (real-time error recovery)
- International Sports Weather Engine (global intelligence)
- Multi-Tier Architecture Engine (reliability framework)
- Business Intelligence Suite (analytics and reporting)

Features:
- Unified command interface
- Cross-system dependency management
- Intelligent scheduling and coordination
- Comprehensive health monitoring
- Automatic failover and recovery
- Global performance optimization

Author: EQ12 Quantum Development Team
Version: 2.0.0 - Unified Integration
Date: November 7, 2025
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class SystemStatus(Enum):
    """System status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class SystemPriority(Enum):
    """System priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class EQ12System:
    """EQ12 system configuration."""
    system_id: str
    system_name: str
    script_path: str
    priority: SystemPriority
    status: SystemStatus
    dependencies: List[str]
    health_score: float
    last_run: Optional[datetime]
    run_interval_minutes: int
    auto_restart: bool
    process_id: Optional[int] = None


class EQ12UnifiedLauncher:
    """Unified system integration and orchestration launcher."""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.scripts_path = self.workspace_path / "scripts"
        self.logs_path = self.workspace_path / "logs"
        self.data_path = self.workspace_path / "data"
        
        # Ensure directories exist
        for path in [self.logs_path, self.data_path]:
            path.mkdir(exist_ok=True)
        
        # Setup logging
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_path / f"unified_launcher_{self.timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize systems registry
        self.systems = self._initialize_systems_registry()
        self.running_processes = {}
        
        # Performance tracking
        self.system_metrics = {}
        self.global_health_score = 0.0
    
    def _initialize_systems_registry(self) -> List[EQ12System]:
        """Initialize the EQ12 systems registry."""
        systems = [
            EQ12System(
                system_id="daily_maintenance",
                system_name="Daily Maintenance Pack",
                script_path="eq12_daily_maintenance.py",
                priority=SystemPriority.CRITICAL,
                status=SystemStatus.OFFLINE,
                dependencies=[],
                health_score=100.0,
                last_run=None,
                run_interval_minutes=1440,  # 24 hours
                auto_restart=True
            ),
            EQ12System(
                system_id="self_healing",
                system_name="Self-Healing Orchestrator",
                script_path="eq12_self_healing_orchestrator.py",
                priority=SystemPriority.CRITICAL,
                status=SystemStatus.OFFLINE,
                dependencies=[],
                health_score=100.0,
                last_run=None,
                run_interval_minutes=5,  # 5 minutes
                auto_restart=True
            ),
            EQ12System(
                system_id="international_weather",
                system_name="International Sports Weather Engine",
                script_path="eq12_international_sports_weather_engine.py",
                priority=SystemPriority.HIGH,
                status=SystemStatus.OFFLINE,
                dependencies=["daily_maintenance"],
                health_score=100.0,
                last_run=None,
                run_interval_minutes=60,  # 1 hour
                auto_restart=True
            ),
            EQ12System(
                system_id="multi_tier_architecture",
                system_name="Multi-Tier Architecture Engine",
                script_path="eq12_multi_tier_architecture_engine.py",
                priority=SystemPriority.HIGH,
                status=SystemStatus.OFFLINE,
                dependencies=["self_healing"],
                health_score=100.0,
                last_run=None,
                run_interval_minutes=30,  # 30 minutes
                auto_restart=True
            ),
            EQ12System(
                system_id="business_intelligence",
                system_name="Business Intelligence Strategy",
                script_path="eq12_business_intelligence_prompt_pack_generator.py",
                priority=SystemPriority.MEDIUM,
                status=SystemStatus.OFFLINE,
                dependencies=["international_weather"],
                health_score=100.0,
                last_run=None,
                run_interval_minutes=720,  # 12 hours
                auto_restart=False
            ),
            EQ12System(
                system_id="revenue_accelerator",
                system_name="Revenue Scale Accelerator",
                script_path="eq12_revenue_scale_accelerator.py",
                priority=SystemPriority.MEDIUM,
                status=SystemStatus.OFFLINE,
                dependencies=["business_intelligence"],
                health_score=100.0,
                last_run=None,
                run_interval_minutes=360,  # 6 hours
                auto_restart=False
            )
        ]
        
        return systems
    
    async def start_system(self, system_id: str) -> Dict[str, Any]:
        """Start an individual EQ12 system."""
        system = next((s for s in self.systems if s.system_id == system_id), None)
        
        if not system:
            return {"success": False, "error": f"System {system_id} not found"}
        
        self.logger.info(f" Starting {system.system_name}...")
        print(f" Starting {system.system_name}...")
        
        # Check dependencies
        for dep_id in system.dependencies:
            dep_system = next((s for s in self.systems if s.system_id == dep_id), None)
            if dep_system and dep_system.status != SystemStatus.ONLINE:
                self.logger.warning(f" Dependency {dep_system.system_name} not online")
                # Auto-start dependency
                await self.start_system(dep_id)
        
        # Construct script path
        script_full_path = self.scripts_path / system.script_path
        
        if not script_full_path.exists():
            error_msg = f"Script not found: {script_full_path}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Start the system process
            system.status = SystemStatus.STARTING
            
            # Execute Python script
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_full_path), "--workspace", str(self.workspace_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Store process reference
            self.running_processes[system_id] = process
            system.process_id = process.pid
            system.status = SystemStatus.ONLINE
            system.last_run = datetime.now(timezone.utc)
            
            self.logger.info(f" {system.system_name} started (PID: {process.pid})")
            print(f" {system.system_name} started (PID: {process.pid})")
            
            return {
                "success": True,
                "system_id": system_id,
                "process_id": process.pid,
                "status": system.status.value
            }
            
        except Exception as e:
            system.status = SystemStatus.ERROR
            error_msg = f"Failed to start {system.system_name}: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def stop_system(self, system_id: str) -> Dict[str, Any]:
        """Stop an individual EQ12 system."""
        system = next((s for s in self.systems if s.system_id == system_id), None)
        
        if not system:
            return {"success": False, "error": f"System {system_id} not found"}
        
        self.logger.info(f" Stopping {system.system_name}...")
        print(f" Stopping {system.system_name}...")
        
        try:
            if system_id in self.running_processes:
                process = self.running_processes[system_id]
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    await asyncio.wait_for(process.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    # Force kill if necessary
                    process.kill()
                    await process.wait()
                
                del self.running_processes[system_id]
            
            system.status = SystemStatus.OFFLINE
            system.process_id = None
            
            self.logger.info(f" {system.system_name} stopped")
            print(f" {system.system_name} stopped")
            
            return {"success": True, "system_id": system_id}
            
        except Exception as e:
            error_msg = f"Failed to stop {system.system_name}: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def check_system_health(self, system_id: str) -> Dict[str, Any]:
        """Check health of an individual EQ12 system."""
        system = next((s for s in self.systems if s.system_id == system_id), None)
        
        if not system:
            return {"health_score": 0.0, "status": "not_found"}
        
        health_data = {
            "system_id": system_id,
            "system_name": system.system_name,
            "status": system.status.value,
            "health_score": 100.0,
            "process_id": system.process_id,
            "last_run": system.last_run.isoformat() if system.last_run else None,
            "checks": {
                "process_running": False,
                "dependencies_healthy": True,
                "script_exists": False,
                "recent_activity": False
            }
        }
        
        # Check if script exists
        script_path = self.scripts_path / system.script_path
        health_data["checks"]["script_exists"] = script_path.exists()
        
        # Check if process is running
        if system_id in self.running_processes:
            process = self.running_processes[system_id]
            health_data["checks"]["process_running"] = process.returncode is None
        
        # Check dependencies
        for dep_id in system.dependencies:
            dep_system = next((s for s in self.systems if s.system_id == dep_id), None)
            if dep_system and dep_system.status != SystemStatus.ONLINE:
                health_data["checks"]["dependencies_healthy"] = False
                break
        
        # Check recent activity
        if system.last_run:
            time_since_run = datetime.now(timezone.utc) - system.last_run
            health_data["checks"]["recent_activity"] = time_since_run.total_seconds() < system.run_interval_minutes * 60 * 2
        
        # Calculate health score
        health_score = 0.0
        checks = health_data["checks"]
        
        if checks["script_exists"]:
            health_score += 25.0
        if checks["process_running"]:
            health_score += 35.0
        if checks["dependencies_healthy"]:
            health_score += 25.0
        if checks["recent_activity"]:
            health_score += 15.0
        
        health_data["health_score"] = health_score
        system.health_score = health_score
        
        return health_data
    
    async def launch_unified_systems(self) -> Dict[str, Any]:
        """Launch all EQ12 systems in proper dependency order."""
        self.logger.info(" Launching unified EQ12 systems...")
        
        print(" EQ12 UNIFIED SYSTEM LAUNCHER")
        print("=" * 35)
        print("Initializing enterprise-grade automation ecosystem...")
        print()
        
        launch_results = {
            "launch_timestamp": datetime.now(timezone.utc).isoformat(),
            "systems_launched": [],
            "systems_failed": [],
            "total_systems": len(self.systems),
            "success_rate": 0.0,
            "global_health_score": 0.0
        }
        
        # Sort systems by priority (critical first)
        priority_order = {
            SystemPriority.CRITICAL: 0,
            SystemPriority.HIGH: 1,
            SystemPriority.MEDIUM: 2,
            SystemPriority.LOW: 3
        }
        
        sorted_systems = sorted(self.systems, key=lambda s: priority_order[s.priority])
        
        # Launch systems in order
        for system in sorted_systems:
            print(f" Launching {system.system_name}...")
            
            start_result = await self.start_system(system.system_id)
            
            if start_result["success"]:
                launch_results["systems_launched"].append(system.system_id)
                print(f"    {system.system_name} online")
            else:
                launch_results["systems_failed"].append({
                    "system_id": system.system_id,
                    "error": start_result.get("error", "Unknown error")
                })
                print(f"    {system.system_name} failed: {start_result.get('error', 'Unknown')}")
            
            # Brief pause between launches
            await asyncio.sleep(1.0)
        
        # Calculate success metrics
        launched_count = len(launch_results["systems_launched"])
        launch_results["success_rate"] = (launched_count / launch_results["total_systems"]) * 100
        
        # Check overall health
        health_scores = []
        for system in self.systems:
            health_data = await self.check_system_health(system.system_id)
            health_scores.append(health_data["health_score"])
        
        launch_results["global_health_score"] = sum(health_scores) / len(health_scores) if health_scores else 0.0
        self.global_health_score = launch_results["global_health_score"]
        
        print(f"\n UNIFIED LAUNCH COMPLETE!")
        print(f" Systems Launched: {launched_count}/{launch_results['total_systems']}")
        print(f" Success Rate: {launch_results['success_rate']:.1f}%")
        print(f" Global Health: {launch_results['global_health_score']:.1f}%")
        
        # Save launch report
        launch_file = self.logs_path / f"unified_launch_{self.timestamp}.json"
        with open(launch_file, 'w', encoding='utf-8') as f:
            json.dump(launch_results, f, indent=2, ensure_ascii=False)
        
        return launch_results
    
    async def monitor_unified_systems(self) -> Dict[str, Any]:
        """Monitor all running EQ12 systems."""
        print("\n UNIFIED SYSTEMS MONITORING")
        print("=" * 32)
        
        monitoring_data = {
            "monitoring_timestamp": datetime.now(timezone.utc).isoformat(),
            "system_health": {},
            "global_metrics": {
                "systems_online": 0,
                "systems_offline": 0,
                "systems_error": 0,
                "average_health": 0.0
            },
            "alerts": []
        }
        
        health_scores = []
        
        for system in self.systems:
            health_data = await self.check_system_health(system.system_id)
            monitoring_data["system_health"][system.system_id] = health_data
            health_scores.append(health_data["health_score"])
            
            # Count system statuses
            if system.status == SystemStatus.ONLINE:
                monitoring_data["global_metrics"]["systems_online"] += 1
            elif system.status == SystemStatus.ERROR:
                monitoring_data["global_metrics"]["systems_error"] += 1
            else:
                monitoring_data["global_metrics"]["systems_offline"] += 1
            
            # Generate alerts
            if health_data["health_score"] < 50:
                monitoring_data["alerts"].append(f"CRITICAL: {system.system_name} health at {health_data['health_score']:.1f}%")
            elif health_data["health_score"] < 80:
                monitoring_data["alerts"].append(f"WARNING: {system.system_name} health at {health_data['health_score']:.1f}%")
            
            # Display status
            status_icon = "" if system.status == SystemStatus.ONLINE else ""
            print(f"{status_icon} {system.system_name}: {health_data['health_score']:.1f}% ({system.status.value})")
        
        # Calculate global metrics
        monitoring_data["global_metrics"]["average_health"] = sum(health_scores) / len(health_scores) if health_scores else 0.0
        self.global_health_score = monitoring_data["global_metrics"]["average_health"]
        
        print(f"\n Global Health: {monitoring_data['global_metrics']['average_health']:.1f}%")
        print(f" Online: {monitoring_data['global_metrics']['systems_online']}")
        print(f" Offline: {monitoring_data['global_metrics']['systems_offline']}")
        print(f" Alerts: {len(monitoring_data['alerts'])}")
        
        return monitoring_data
    
    async def shutdown_unified_systems(self) -> Dict[str, Any]:
        """Gracefully shutdown all EQ12 systems."""
        self.logger.info(" Shutting down unified EQ12 systems...")
        
        print("\n UNIFIED SYSTEMS SHUTDOWN")
        print("=" * 30)
        
        shutdown_results = {
            "shutdown_timestamp": datetime.now(timezone.utc).isoformat(),
            "systems_stopped": [],
            "systems_failed": [],
            "shutdown_time": 0.0
        }
        
        start_time = time.time()
        
        # Stop systems in reverse priority order
        priority_order = {
            SystemPriority.LOW: 0,
            SystemPriority.MEDIUM: 1,
            SystemPriority.HIGH: 2,
            SystemPriority.CRITICAL: 3
        }
        
        sorted_systems = sorted(self.systems, key=lambda s: priority_order[s.priority])
        
        for system in sorted_systems:
            if system.status == SystemStatus.ONLINE:
                print(f" Stopping {system.system_name}...")
                
                stop_result = await self.stop_system(system.system_id)
                
                if stop_result["success"]:
                    shutdown_results["systems_stopped"].append(system.system_id)
                else:
                    shutdown_results["systems_failed"].append({
                        "system_id": system.system_id,
                        "error": stop_result.get("error", "Unknown error")
                    })
        
        shutdown_results["shutdown_time"] = time.time() - start_time
        
        print(f"\n Shutdown completed in {shutdown_results['shutdown_time']:.1f} seconds")
        print(f" Systems stopped: {len(shutdown_results['systems_stopped'])}")
        
        return shutdown_results


async def main():
    """Main execution function for unified launcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Unified System Launcher")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--action", choices=["launch", "monitor", "shutdown", "status"], 
                       default="launch", help="Action to perform")
    parser.add_argument("--system", help="Specific system to operate on")
    parser.add_argument("--continuous", action="store_true", help="Continuous monitoring mode")
    args = parser.parse_args()
    
    try:
        # Initialize unified launcher
        launcher = EQ12UnifiedLauncher(args.workspace)
        
        if args.action == "launch":
            if args.system:
                # Launch specific system
                result = await launcher.start_system(args.system)
                print(f"System {args.system}: {'Started' if result['success'] else 'Failed'}")
            else:
                # Launch all systems
                await launcher.launch_unified_systems()
                
                if args.continuous:
                    # Enter continuous monitoring mode
                    print("\n Entering continuous monitoring mode (Ctrl+C to exit)...")
                    try:
                        while True:
                            await asyncio.sleep(60)  # Monitor every minute
                            await launcher.monitor_unified_systems()
                    except KeyboardInterrupt:
                        print("\n Shutting down...")
                        await launcher.shutdown_unified_systems()
        
        elif args.action == "monitor":
            await launcher.monitor_unified_systems()
        
        elif args.action == "shutdown":
            await launcher.shutdown_unified_systems()
        
        elif args.action == "status":
            monitoring_data = await launcher.monitor_unified_systems()
            print(f"\n Global Health Score: {monitoring_data['global_metrics']['average_health']:.1f}%")
        
        return 0
        
    except Exception as e:
        print(f" UNIFIED LAUNCHER ERROR: {e}")
        logging.error(f"Unified launcher error: {e}")
        return 1


if __name__ == "__main__":
    # Ensure proper event loop for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)